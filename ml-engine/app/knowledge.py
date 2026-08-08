"""Herbal Knowledge Engine.

Loads the curated CSV datasets (plants, combinations, diseases) into an
in-memory knowledge base and provides lookups for the predictor, recommender,
and assistant.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PLANTS_FILE = DATA_DIR / "plants.csv"
COMBINATIONS_FILE = DATA_DIR / "combinations.csv"
DISEASES_FILE = DATA_DIR / "diseases.csv"


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=1)
def load_plants() -> list[dict[str, Any]]:
    return [
        {
            "name": row["name"],
            "scientific_name": row["scientific_name"],
            "family": row["family"],
            "region": row["region"],
            "benefits": _split(row["benefits"]),
            "side_effects": _split(row["side_effects"]),
            "toxicity": row["toxicity"],
            "usage": row["usage"],
            "english_name": row.get("english_name", ""),
        }
        for row in _read_csv(PLANTS_FILE)
    ]


@lru_cache(maxsize=1)
def load_combinations() -> list[dict[str, Any]]:
    return [
        {
            "herb_a": row["herb_a"].strip().lower(),
            "herb_b": row["herb_b"].strip().lower(),
            "verdict": row["verdict"],
            "compatibility_score": int(row["compatibility_score"]),
            "safety_score": int(row["safety_score"]),
            "benefit_score": int(row["benefit_score"]),
            "risk_score": int(row["risk_score"]),
            "scientific_confidence": int(row["scientific_confidence"]),
            "benefits": _split(row["benefits"]),
            "risks": _split(row["risks"]),
        }
        for row in _read_csv(COMBINATIONS_FILE)
    ]


@lru_cache(maxsize=1)
def load_diseases() -> list[dict[str, Any]]:
    return [
        {
            "name": row["name"],
            "symptoms": _split(row["symptoms"]),
            "recommended_herbs": _split(row["recommended_herbs"]),
            "avoid_herbs": _split(row["avoid_herbs"]),
        }
        for row in _read_csv(DISEASES_FILE)
    ]


def find_plant(name: str) -> dict[str, Any] | None:
    needle = name.strip().lower()
    for plant in load_plants():
        if plant["name"].strip().lower() == needle:
            return plant
    return None


def find_combination(a: str, b: str) -> dict[str, Any] | None:
    a, b = a.strip().lower(), b.strip().lower()
    for combo in load_combinations():
        if (combo["herb_a"] == a and combo["herb_b"] == b) or (
            combo["herb_a"] == b and combo["herb_b"] == a
        ):
            return combo
    return None


def find_disease(name: str) -> dict[str, Any] | None:
    needle = name.strip().lower()
    for disease in load_diseases():
        if disease["name"].strip().lower() == needle:
            return disease
    return None


def herb_names() -> list[str]:
    return [plant["name"] for plant in load_plants()]
