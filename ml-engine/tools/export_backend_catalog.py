"""Export the merged plant catalog for the Spring backend.

Writes data/plants.csv into a classpath CSV resource the backend DataSeeder
reads so the Analyzer's herb list (served from PostgreSQL) matches the ML
engine's knowledge base.

The backend parses the CSV with a plain comma split, so any comma inside a
field value is replaced with a semicolon here.

Usage:
    python tools/export_backend_catalog.py
"""

from __future__ import annotations

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PLANTS_FILE = DATA_DIR / "plants.csv"
OUT_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "backend"
    / "src"
    / "main"
    / "resources"
    / "herbs_catalog.csv"
)

COLUMNS = [
    "name",
    "scientific_name",
    "family",
    "region",
    "benefits",
    "side_effects",
    "toxicity",
]


def _sanitize(value: str) -> str:
    return value.replace(",", ";").replace("\n", " ").strip()


def main() -> int:
    if not PLANTS_FILE.exists():
        print(f"Missing plants.csv: {PLANTS_FILE}")
        return 1

    with PLANTS_FILE.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([_sanitize(row.get(c, "")) for c in COLUMNS])

    print(f"Wrote {len(rows)} rows to {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
