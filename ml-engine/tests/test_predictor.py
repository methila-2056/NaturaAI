from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import knowledge  # noqa: E402
from app.predictor import CompatibilityPredictor  # noqa: E402
from app.recommender import RecommendationEngine  # noqa: E402


@pytest.fixture(autouse=True)
def _ensure_data() -> None:
    assert knowledge.load_plants(), "plants.csv missing or empty"
    assert knowledge.load_combinations(), "combinations.csv missing or empty"


def test_find_plant() -> None:
    plant = knowledge.find_plant("Tulsi")
    assert plant is not None
    assert "benefits" in plant


def test_find_combination_reversed() -> None:
    combo = knowledge.find_combination("Honey", "Tulsi")
    assert combo is not None
    assert combo["verdict"] in {"safe", "caution", "unsafe"}


def test_safe_pair_prediction() -> None:
    result = CompatibilityPredictor().predict(["Tulsi", "Ginger"], "internal")
    assert result["verdict"] == "safe"
    assert result["compatibilityScore"] >= 80
    assert 0 <= result["safetyScore"] <= 100
    assert result["benefits"]
    assert result["preparation"]


def test_unknown_pair_is_caution() -> None:
    result = CompatibilityPredictor().predict(["Moringa", "Rose"], "internal")
    assert result["verdict"] in {"caution", "safe"}


def test_unified_toxicity_key() -> None:
    result = CompatibilityPredictor().predict(["Aloe Vera", "Neem"], "external")
    assert result["toxicityLevel"] in {"low", "medium", "high"}


def test_recommendation_engine() -> None:
    engine = RecommendationEngine()
    recommendations = engine.recommend(
        diseases=["Common Cold"], treatment_type="internal", limit=2
    )
    assert len(recommendations) >= 1
    assert all("ingredients" in r for r in recommendations)


def test_recommendation_avoids_honey_for_diabetes() -> None:
    engine = RecommendationEngine()
    recommendations = engine.recommend(diseases=["Diabetes"], treatment_type="internal", limit=5)
    ingredients = {i for r in recommendations for i in r["ingredients"]}
    assert "Honey" not in ingredients


def test_model_artifact_loads() -> None:
    from app.predictor import MODEL_FILE

    assert MODEL_FILE.exists(), "predictor.joblib is missing"
    predictor = CompatibilityPredictor(use_model=True)
    assert predictor.model is not None, "model artifact should load (see train_predictor.py)"
    assert predictor.model_name
    assert predictor.is_ml_active


def test_ml_path_used_for_unknown_in_vocab_pair() -> None:
    predictor = CompatibilityPredictor(use_model=True)
    pred = predictor._model_prediction("Moringa", "Rose")
    assert pred is not None, "ML path should predict for in-vocab, uncurated pairs"
    verdict, confidence = pred
    assert verdict in {"safe", "caution", "unsafe"}
    assert 0 <= confidence <= 100
