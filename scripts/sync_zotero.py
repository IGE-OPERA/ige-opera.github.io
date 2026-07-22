#!/usr/bin/env python3
"""Sync the OPERA publications BibTeX file from the public Zotero group library.

Fetches top-level "paper" items from the Zotero Web API (v3) as BibTeX, filters
to publication item types, normalizes the output for deterministic diffs, and
writes _data/publications.bib. Designed to run in CI (GitHub Actions) with no
authentication (the group library is public) and no third-party packages.

Safety: if any request fails or zero entries are returned, the script aborts
without writing, so an API error can not overwrite the publications page.
"""

from __future__ import annotations

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
