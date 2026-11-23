#!/usr/bin/env python3
"""Sync the OPERA publications BibTeX file from the public Zotero group library.

Fetches top-level "paper" items from the Zotero Web API (v3) as BibTeX, filters
to publication item types, normalizes the output for deterministic diffs, and
writes _data/publications.bib. Designed to run in CI (GitHub Actions) with no
authentication (the group library is public) and no third-party packages.

Additionally fetches the same items as JSON and writes
_data/publications.json — the source of the publication page cards — and
reports newly added papers through the `new_papers` GitHub Actions output so
the workflow can open a "papers to summarise with llm4pills" issue.

Safety: if any request fails or zero entries are returned, the script aborts
without writing, so an API error can not overwrite the publications page.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# --- Configuration -----------------------------------------------------------

GROUP_ID = os.environ.get("ZOTERO_GROUP_ID", "6427155")
API_BASE = "https://api.zotero.org"
OUTPUT_PATH = os.environ.get(
    "ZOTERO_OUTPUT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "_data", "publications.bib"),
)

# "Papers only" scope
ITEM_TYPES = " || ".join(
    [
        "journalArticle",
        "conferencePaper",
        "bookSection",
        "book",
        "preprint",
        "report",
        "thesis",
    ]
)

PAGE_SIZE = 100          # Zotero max per request
MAX_RETRIES = 5          # per-request retry budget
# Fields dropped from every entry before writing
DROP_FIELDS = ["abstract", "note"]

USER_AGENT = "ige-opera-zotero-sync/1.0 (+https://ige-opera.github.io)"


# --- HTTP --------------------------------------------------------------------

def _request(start: int) -> tuple[str, int]:
    """Fetch one page of BibTeX. Returns (body, total_results)."""
    query = urllib.parse.urlencode(
        {
            "format": "bibtex",
            "itemType": ITEM_TYPES,
            "limit": PAGE_SIZE,
            "start": start,
        }
    )
    url = f"{API_BASE}/groups/{GROUP_ID}/items/top?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                # Honor a server-requested cool-down before the *next* request.
                backoff = resp.headers.get("Backoff")
                if backoff:
                    time.sleep(_to_int(backoff, default=1))
                total = _to_int(resp.headers.get("Total-Results"), default=0)
                body = resp.read().decode("utf-8")
                return body, total
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < MAX_RETRIES:
                wait = _to_int(exc.headers.get("Retry-After"), default=2 ** attempt)
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise

    raise RuntimeError(f"Failed to fetch start={start} after {MAX_RETRIES} attempts")


def fetch_all() -> str:
    """Fetch and concatenate every page of BibTeX from the group library."""
    body, total = _request(start=0)
    chunks = [body]
    fetched = _count_entries(body)
    start = PAGE_SIZE
    while start < total:
        page_body, _ = _request(start=start)
        chunks.append(page_body)
        fetched += _count_entries(page_body)
        start += PAGE_SIZE
    return "\n".join(chunks)


# --- BibTeX parsing / normalization ------------------------------------------

_ENTRY_START = re.compile(r"@\s*[A-Za-z]+\s*\{", re.MULTILINE)


def split_entries(bibtex: str) -> list[str]:
    """Split a BibTeX string into individual balanced @entry{...} blocks."""
    entries: list[str] = []
    for match in _ENTRY_START.finditer(bibtex):
        start = match.start()
        # Walk from the opening brace, balancing braces to find the entry end.
        depth = 0
        i = bibtex.index("{", match.end() - 1)
        for j in range(i, len(bibtex)):
            ch = bibtex[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    entries.append(bibtex[start : j + 1])
                    break
    return entries


def cite_key(entry: str) -> str:
    """Extract the cite key from an @type{key, ... entry."""
    m = re.search(r"@\s*[A-Za-z]+\s*\{\s*([^,\s]+)\s*,", entry)
    return m.group(1) if m else ""


def strip_field(entry: str, field: str) -> str:
    """Remove a top-level `field = {...}` or `field = "..."` from an entry."""
    m = re.search(r'(^|,)\s*' + re.escape(field) + r'\s*=\s*', entry, re.IGNORECASE)
    if not m:
        return entry
    val_start = m.end()
    opener = entry[val_start] if val_start < len(entry) else ""
    if opener not in "{\"":
        return entry
    depth = 0
    end = None
    for k in range(val_start, len(entry)):
        ch = entry[k]
        if opener == "{":
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = k + 1
                    break
        else:  # quoted value
            if ch == "\"" and k > val_start:
                end = k + 1
                break
    if end is None:
        return entry
    # Drop the field plus a trailing comma if present.
    tail = entry[end:]
    tail = re.sub(r"^\s*,", "", tail, count=1)
    return entry[: m.start()] + ("," if m.group(1) == "," else "") + tail


def normalize(bibtex: str) -> str:
    """Produce a deterministic BibTeX string: drop fields, sorted by key."""
    entries = split_entries(bibtex)
    for field in DROP_FIELDS:
        entries = [strip_field(e, field) for e in entries]
    entries = [e.strip() for e in entries if cite_key(e)]
    entries.sort(key=lambda e: cite_key(e).lower())
    return "\n\n".join(entries) + "\n"


# --- Publications JSON feed (for the publication page cards) ------------------

JSON_OUTPUT_PATH = os.environ.get(
    "ZOTERO_JSON_OUTPUT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "_data", "publications.json"),
)


def _request_json(start: int) -> tuple[list[dict], int]:
    """Fetch one page of item JSON. Returns (items, total_results)."""
    query = urllib.parse.urlencode(
        {
            "format": "json",
            "itemType": ITEM_TYPES,
            "limit": PAGE_SIZE,
            "start": start,
        }
    )
    url = f"{API_BASE}/groups/{GROUP_ID}/items/top?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = _to_int(resp.headers.get("Total-Results"), default=0)
                body = resp.read().decode("utf-8")
                return json.loads(body), total
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError(f"Failed to fetch JSON start={start}")


def fetch_json_all() -> list[dict]:
    items, total = _request_json(start=0)
    start = PAGE_SIZE
    while start < total:
        page_items, _ = _request_json(start=start)
        items.extend(page_items)
        start += PAGE_SIZE
    return items


def _people_pub_ids() -> set[str]:
    """Collect pub_id values from _people/*.md so members render in bold."""
    pub_ids: set[str] = set()
    people_dir = os.path.join(os.path.dirname(__file__), "..", "_people")
    if not os.path.isdir(people_dir):
        return pub_ids
    for name in os.listdir(people_dir):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(people_dir, name), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r'pub_id:\s*"([^"]+)"', line.strip())
                if m:
                    pub_ids.add(_norm_name(m.group(1)))
    return pub_ids


def _norm_name(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def _author_string(creator: dict) -> str:
    """'Family, F.' from a Zotero creator, or the name as-is for organisations."""
    if "name" in creator:
        return creator["name"]
    family = creator.get("lastName", "").strip()
    given = creator.get("firstName", "").strip()
    initials = " ".join(f"{part[0]}." for part in given.split() if part)
    return f"{family}, {initials}" if initials else family


def build_publications(items: list[dict]) -> list[dict]:
    """Reduce Zotero item JSON to the flat structure the site reads."""
    pub_ids = _people_pub_ids()
    pubs: list[dict] = []

    for item in items:
        d = item.get("data", {})
        title = (d.get("title") or "").strip()
        if not title or d.get("itemType") in ("attachment", "note"):
            continue
        date = (d.get("date") or "").strip()
        year = None
        month = None
        m = re.search(r"(\d{4})", date)
        if m:
            year = int(m.group(1))
        m = re.search(r"\d{4}[-/](\d{1,2})", date)
        if m:
            month = int(m.group(1))

        authors = []
        for c in d.get("creators", []):
            if c.get("creatorType") not in ("author", None):
                continue
            name = _author_string(c)
            authors.append(
                {"name": name, "member": _norm_name(name) in pub_ids}
            )

        pubs.append(
            {
                "key": d.get("key") or item.get("key") or "",
                "type": d.get("itemType") or "article",
                "title": title,
                "authors": authors,
                "year": year,
                "month": month,
                "journal": (d.get("publicationTitle") or "").strip(),
                "volume": (d.get("volume") or "").strip(),
                "issue": (d.get("issue") or "").strip(),
                "pages": (d.get("pages") or "").strip(),
                "publisher": (d.get("publisher") or "").strip(),
                "doi": (d.get("DOI") or "").strip(),
                "url": (d.get("url") or "").strip(),
            }
        )

    pubs.sort(key=lambda p: (p["year"] or 0, p["month"] or 0, p["title"].lower()))
    pubs.reverse()
    return pubs


def _load_existing_keys(json_path: str) -> set[str]:
    keys: set[str] = set()
    if not os.path.exists(json_path):
        return keys
    try:
        with open(json_path, encoding="utf-8") as fh:
            for p in json.load(fh):
                keys.add(p.get("key", ""))
    except (json.JSONDecodeError, OSError):
        pass
    return keys


# --- Helpers -----------------------------------------------------------------

def _to_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _count_entries(bibtex: str) -> int:
    return len(_ENTRY_START.findall(bibtex))


# --- Main --------------------------------------------------------------------

def main() -> int:
    try:
        raw = fetch_all()
    except Exception as exc:  # noqa: BLE001 - abort on any fetch failure
        print(f"ERROR: failed to fetch from Zotero: {exc}", file=sys.stderr)
        return 1

    output = normalize(raw)
    entry_count = _count_entries(output)

    # Safety guard: never overwrite the page with an empty/failed result.
    if entry_count == 0:
        print("ERROR: fetched 0 entries; refusing to overwrite the bib file.",
              file=sys.stderr)
        return 1

    out_path = os.path.abspath(OUTPUT_PATH)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(output)

    print(f"Wrote {entry_count} entries to {out_path}")

    # --- JSON feed for the publication page cards ------------------------------

    json_path = os.path.abspath(JSON_OUTPUT_PATH)
    try:
        items = fetch_json_all()
    except Exception as exc:  # noqa: BLE001 - abort on any fetch failure
        print(f"ERROR: failed to fetch JSON from Zotero: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("ERROR: fetched 0 JSON items; refusing to overwrite the json feed.",
              file=sys.stderr)
        return 1

    pubs = build_publications(items)
    if not pubs:
        print("ERROR: no usable publications in the JSON feed; refusing to write.",
              file=sys.stderr)
        return 1

    known = _load_existing_keys(json_path)
    new_papers = [
        {"key": p["key"], "title": p["title"], "doi": p["doi"], "url": p["url"]}
        for p in pubs
        if p["key"] not in known
    ]

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(pubs, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Wrote {len(pubs)} publications to {json_path}")

    # GitHub Actions output: list of new papers for the pills runbook.
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write(f"new_papers={json.dumps(new_papers, ensure_ascii=False)}\n")
    if new_papers:
        print("New papers (need llm4pills one-liners):")
        for p in new_papers:
            print(f"  - {p['title']} (doi:{p['doi']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
