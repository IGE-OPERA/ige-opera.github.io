#!/usr/bin/env python3
"""Fetch banner artwork for the publication page cards.

For every publication in _data/publications.json that has a DOI, this script
follows the DOI to the publisher landing page, reads its `og:image` social
preview (in practice the article's first figure) and downloads it to
assets/images/publications/. The resulting mapping is written to
_data/artwork.json, which the publication template reads.

Best effort by design: entries whose landing page has no fetchable preview
simply get no banner (the card renders a typographic fallback). Failures per
entry are warnings; the script only fails when its inputs are unreadable.

Usage:
    python3 scripts/fetch_publication_artwork.py [--max N] [--refresh]
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLICATIONS_PATH = os.path.join(REPO_ROOT, "_data", "publications.json")
ARTWORK_JSON_PATH = os.path.join(REPO_ROOT, "_data", "artwork.json")
ARTWORK_DIR = os.path.join(REPO_ROOT, "assets", "images", "publications")

USER_AGENT = "ige-opera-artwork-fetch/1.0 (+https://ige-opera.github.io)"
TIMEOUT = 45
MAX_BYTES = 8 * 1024 * 1024

_OG_IMAGE = re.compile(
    rb'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_OG_IMAGE_REV = re.compile(
    rb'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.IGNORECASE,
)


def _fetch(url: str) -> bytes:
    safe = _safe_url(url)
    req = urllib.request.Request(safe, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def _safe_url(url: str) -> str:
    """Re-encode URLs read from web pages (they may contain raw spaces)."""
    parts = urllib.parse.urlsplit(url.strip())
    return urllib.parse.urlunsplit(
        (
            parts.scheme or "https",
            parts.netloc,
            urllib.parse.quote(parts.path),
            parts.query,
            parts.fragment,
        )
    )


def _landing_url(doi: str) -> str:
    return f"https://doi.org/{urllib.parse.quote(doi)}"


def find_og_image(doi: str) -> str | None:
    """Follow the DOI and read the og:image preview of the landing page."""
    for attempt in range(2):
        try:
            body = _fetch(_landing_url(doi))
            m = _OG_IMAGE.search(body) or _OG_IMAGE_REV.search(body)
            if m:
                url = m.group(1).decode("utf-8", "replace").replace("&amp;", "&")
                return url
            return None
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 0:
                continue
            return None
    return None


def extension_for(url: str, content_type: str) -> str:
    path_ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if path_ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".tif", ".tiff"):
        return ".jpg" if path_ext == ".jpeg" else path_ext
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    return ".png"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=0,
                        help="fetch at most N new banners (0 = no limit)")
    parser.add_argument("--refresh", action="store_true",
                        help="also refetch entries already having artwork")
    args = parser.parse_args()

    if not os.path.exists(PUBLICATIONS_PATH):
        print("ERROR: _data/publications.json missing; run scripts/sync_zotero.py first.",
              file=sys.stderr)
        return 1

    with open(PUBLICATIONS_PATH, encoding="utf-8") as fh:
        pubs = json.load(fh)

    artwork: dict[str, str] = {}
    if os.path.exists(ARTWORK_JSON_PATH):
        with open(ARTWORK_JSON_PATH, encoding="utf-8") as fh:
            artwork = json.load(fh)

    os.makedirs(ARTWORK_DIR, exist_ok=True)
    fetched = kept = failed = skipped = 0

    for pub in pubs:
        key = pub.get("key") or ""
        doi = pub.get("doi") or ""
        if not key:
            continue
        if key in artwork and not args.refresh:
            # keep existing mapping; verify the file is still there
            if os.path.exists(os.path.join(REPO_ROOT, artwork[key].lstrip("/"))):
                kept += 1
                continue
        if not doi:
            skipped += 1
            continue
        if args.max and fetched >= args.max:
            break

        og = find_og_image(doi)
        if not og:
            print(f"  no og:image: {pub.get('title', '')[:60]} ({doi})")
            failed += 1
            continue
        try:
            body = _fetch(og)
        except Exception as exc:  # noqa: BLE001 - one bad entry must not stop the batch
            print(f"  download failed: {og} ({exc})")
            failed += 1
            continue
        if len(body) > MAX_BYTES:
            print(f"  too large ({len(body)} bytes), skipping: {og}")
            failed += 1
            continue
        ext = extension_for(og, "")
        with open(os.path.join(ARTWORK_DIR, key + ext), "wb") as fh:
            fh.write(body)
        rel = f"assets/images/publications/{key}{ext}"
        artwork[key] = f"/{rel}"
        fetched += 1
        print(f"  fetched: {rel}")

    # Drop mappings whose files vanished (e.g. images committed then removed).
    artwork = {
        k: v
        for k, v in artwork.items()
        if os.path.exists(os.path.join(REPO_ROOT, v.lstrip("/")))
    }

    with open(ARTWORK_JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(artwork, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    print(
        f"artwork: fetched={fetched} kept={kept} failed={failed} "
        f"skipped(no doi)={skipped} -> {os.path.relpath(ARTWORK_JSON_PATH, REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
