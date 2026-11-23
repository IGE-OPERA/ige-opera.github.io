#!/usr/bin/env python3
"""Generate the climate "warming stripes" strip used on the OPERA home page.

Fetches global annual mean surface temperature anomalies (J-D column of the
GISTEMP v4 "Global-mean monthly, seasonal, and annual means" table, a public
domain NASA dataset), bins each year's anomaly into the classic stripes palette
and writes a compact standalone SVG.

Run: python3 scripts/make_warming_stripes.py
Output: assets/images/home/climate-stripes.svg
"""

from __future__ import annotations

import csv
import io
import os
import ssl
import sys
import urllib.request

DATA_URL = (
    "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
)
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.abspath(
    os.path.join(HERE, "..", "assets", "images", "home", "climate-stripes.svg")
)

# Classic warming-stripes palette (Hawkins, showyourstripes.info style):
# 8 blues -> near-white center -> 8 reds.
PALETTE = [
    "#08306b", "#08519c", "#2171b5", "#4292c6",
    "#6baed6", "#9ecae1", "#c6dbef", "#deebf7",
    "#f7f7f7",
    "#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a",
    "#ef3b2c", "#cb181d", "#a50f15", "#67000d",
]
CENTER = 8  # index of the near-white middle bin
SCALE = 1.25  # anomaly (deg C) mapped to the extreme bins

BAR_WIDTH = 10
BAR_HEIGHT = 64


def fetch_anomalies() -> list[tuple[int, float]]:
    """Return [(year, anomaly)] from the GISTEMP annual table."""
    # NASA's static CSV is served with a strict TLS configuration that some
    # local Python builds reject; fall back gracely.
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(DATA_URL, timeout=60, context=context) as resp:
            text = resp.read().decode("utf-8-sig")
    except Exception:
        with urllib.request.urlopen(DATA_URL, timeout=60) as resp:
            text = resp.read().decode("utf-8-sig")

    rows: list[tuple[int, float]] = []
    reader = csv.reader(io.StringIO(text))
    for i, row in enumerate(reader):
        if not row or not row[0].strip().isdigit():
            continue
        year = int(row[0])
        header = None
        # The CSV has a header row with column names; find the "J-D" column
        # once from the first matching row.
        if header is None:
            header_row = [c.strip().lower() for c in row]
            marker = header_row  # noqa: F841 - readability
        try:
            jd = float(row[header_row.index("j-d")] if "j-d" in header_row else row[13])
        except (ValueError, IndexError):
            continue
        rows.append((year, jd))
    return rows


def anomaly_to_color(anomaly: float) -> str:
    """Bin an anomaly into the palette, symmetric around 0."""
    n_side = CENTER  # bins on each side of the center
    frac = max(-1.0, min(1.0, anomaly / SCALE))
    idx = int(round(frac * n_side))  # -n_side..n_side
    return PALETTE[CENTER + idx]


def main() -> int:
    data = fetch_anomalies()
    if len(data) < 50:
        print(f"ERROR: only {len(data)} years fetched; refusing to write.",
              file=sys.stderr)
        return 1

    width = len(data) * BAR_WIDTH
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {BAR_HEIGHT}" '
        f'width="{width}" height="{BAR_HEIGHT}" preserveAspectRatio="none" '
        f'role="img" aria-label="Warming stripes {data[0][0]} to {data[-1][0]}">'
    ]
    for i, (year, anomaly) in enumerate(data):
        color = anomaly_to_color(anomaly)
        parts.append(
            f'<rect x="{i * BAR_WIDTH}" y="0" width="{BAR_WIDTH}" '
            f'height="{BAR_HEIGHT}" fill="{color}"/>'
        )
    parts.append("</svg>")
    svg = "".join(parts)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"Wrote {len(data)} years ({data[0][0]}-{data[-1][0]}) to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
