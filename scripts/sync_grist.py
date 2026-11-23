#!/usr/bin/env python3
"""Sync OPERA website content from the Grist content database.

Pulls the Projects, Outreach, News and Positions tables from the group's Grist
document (https://grist.numerique.gouv.fr), downloads image attachments, and
writes the data files the website reads:

    _data/projects.yml, _data/outreach.yml,
    _data/news.yml, _data/positions.yml

Local layout: Grist becomes the friendlier editing interface; the website
still builds from plain YAML files committed to the repository. If Grist is
unreachable or a table fetch fails, this script aborts without writing, so the
website keeps its last known good content.

Usage (needs the doc id and an API key):

    GRIST_API_KEY=... GRIST_DOC_ID=... python3 scripts/sync_grist.py

For the expected Grist column names, see docs/grist-setup.md.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# --- Configuration -----------------------------------------------------------

GRIST_BASE_URL = os.environ.get("GRIST_BASE_URL", "https://grist.numerique.gouv.fr")
GRIST_DOC_ID = os.environ.get("GRIST_DOC_ID", "")
GRIST_API_KEY = os.environ.get("GRIST_API_KEY", "")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "_data")

USER_AGENT = "ige-opera-grist-sync/1.0 (+https://ige-opera.github.io)"
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60

# Table name in Grist -> (output data file, per-table configuration)
TABLES: dict[str, dict] = {
    "Projects": {
        "file": "projects.yml",
        "image_dir": os.path.join(REPO_ROOT, "assets", "images", "projects"),
    },
    "Outreach": {
        "file": "outreach.yml",
        "image_dir": os.path.join(REPO_ROOT, "assets", "images", "outreach"),
    },
    "News": {"file": "news.yml"},
    "Positions": {"file": "positions.yml"},
}

#Site field <- Grist column
FIELD_MAP = {
    "Projects": {
        "title": "title",
        "excerpt": "excerpt",
        "url": "url",
        "btn_label": "btn_label",
        "image": "image",
        "status": "status",
        "contact": "contact",
        "sort": "sort",
    },
    "Outreach": {
        "title": "title",
        "excerpt": "excerpt",
        "url": "url",
        "image": "image",
        "sort": "sort",
    },
    "News": {
        "date": "date",
        "title": "title",
        "text": "text",
        "url": "url",
        "url_label": "url_label",
    },
    "Positions": {
        "title": "title",
        "excerpt": "excerpt",
        "url": "url",
        "status": "status",
        "type": "type",
        "contact": "contact",
        "deadline": "deadline",
    },
}

# --- HTTP --------------------------------------------------------------------

class GristError(Exception):
    pass


def _grist_request(path: str) -> bytes:
    """GET a Grist API endpoint with the standard headers, with retries."""
    if not GRIST_API_KEY or not GRIST_DOC_ID:
        raise GristError(
            "GRIST_DOC_ID and GRIST_API_KEY must be set "
            "(create a key in Grist: Personal Settings -> API keys)"
        )
    url = f"{GRIST_BASE_URL}/api/docs/{GRIST_DOC_ID}/{path.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GRIST_API_KEY}",
            "User-Agent": USER_AGENT,
        },
    )
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                last_exc = exc
                continue
            raise GristError(f"{url} -> HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                last_exc = exc
                continue
            raise GristError(f"{url} -> {exc}") from exc
    raise GristError(f"{url} failed after {MAX_RETRIES} attempts: {last_exc}")


def fetch_records(table: str) -> list[dict]:
    """Fetch all records of a Grist table, as a list of field dicts."""
    body = _grist_request(f"tables/{urllib.parse.quote(table)}/records")
    payload = json.loads(body.decode("utf-8"))
    records = payload.get("records", [])
    return [dict(r.get("fields", {})) for r in records]


def download_attachment(field_value, image_dir: str, stem: str) -> str | None:
    """Download a Grist attachment to image_dir, return its relative path.

    A Grist attachment cell holds a list like
    [{"id": 17, "fileName": "logo.png", "size": ...}] (or may be None).
    """
    if not field_value:
        return None
    atts = field_value if isinstance(field_value, list) else [field_value]
    att = atts[0]
    att_id = att.get("id") if isinstance(att, dict) else None
    if att_id is None:
        return None
    file_name = att.get("fileName") or f"{stem}.png"
    file_name = re.sub(r"[^A-Za-z0-9._-]", "_", file_name)
    os.makedirs(image_dir, exist_ok=True)
    out_path = os.path.join(image_dir, file_name)
    if os.path.exists(out_path):
        return os.path.relpath(out_path, REPO_ROOT).replace(os.sep, "/")
    body = _grist_request(f"attachments/{att_id}/download")
    with open(out_path, "wb") as fh:
        fh.write(body)
    return os.path.relpath(out_path, REPO_ROOT).replace(os.sep, "/")


# --- YAML writing (stdlib; JSON strings are valid YAML scalars) --------------

def yaml_scalar(value) -> str:
    if value is None or value == "":
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    # Multi-line tabs in Grist become <br> for the card markdown renderer.
    if "\n" in text:
        text = text.replace("\r", "").replace("\n", " <br> ")
    return json.dumps(text, ensure_ascii=False)


def write_table_yaml(table: str, rows: list[dict]) -> str:
    """Render and write one table's data file. Returns written path."""
    cfg = TABLES[table]
    fmap = FIELD_MAP[table]

    out_lines: list[str] = []
    for fields in rows:
        entry: list[str] = []
        image_path = None
        for site_field, grist_col in fmap.items():
            value = fields.get(grist_col)
            if grist_col == "image":
                continue  # handled separately below
            if site_field == "date":
                date = str(value or "")[:10]  # ISO date from Gist Date cell
                if date:
                    entry.append(f'  date: "{date}"')
                continue
            if site_field == "deadline":
                deadline = str(value or "")[:10]
                if deadline:
                    entry.append(f'  deadline: "{deadline}"')
                continue
            if value is not None and value != "":
                entry.append(f'  {site_field}: {yaml_scalar(value)}')
        # Image attachment column
        if "image" in fmap:
            downloaded = download_attachment(
                fields.get("image"), cfg["image_dir"],
                stem=str(fields.get("title") or table).lower().replace(" ", "-"),
            )
            if downloaded:
                entry.append(f'  image_path: "/{downloaded}"')
        if not any(line.startswith("  title:") for line in entry):
            continue  # skip junk rows without a title
        out_lines.append("- " + entry[0].strip())
        out_lines.extend(entry[1:])
        out_lines.append("")

    content = "\n".join(out_lines) if out_lines else "[]\n"
    out_path = os.path.join(DATA_DIR, cfg["file"])
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return out_path


# --- Main --------------------------------------------------------------------

def main() -> int:
    if not GRIST_API_KEY or not GRIST_DOC_ID:
        print(
            "ERROR: set GRIST_DOC_ID and GRIST_API_KEY (see docs/grist-setup.md).",
            file=sys.stderr,
        )
        return 1

    tables = os.environ.get("GRIST_TABLES", " ".join(TABLES)).split()
    written: list[str] = []
    try:
        for table in tables:
            if table not in TABLES:
                print(f"WARNING: unknown table {table}, skipping.", file=sys.stderr)
                continue
            rows = fetch_records(table)
            print(f"{table}: fetched {len(rows)} records")
            path = write_table_yaml(table, rows)
            written.append(path)
    except GristError as exc:
        print(f"ERROR: Grist sync failed, nothing written: {exc}", file=sys.stderr)
        return 1

    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
