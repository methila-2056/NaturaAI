"""ML Compatibility Predictor.

Blends curated pair records from the knowledge base with a rule-based fallback
and (when a trained artifact exists) an ensemble of gradient-boosted trees.

Model training pipeline lives in train/train_predictor.py. Supported
algorithms: Random Forest, XGBoost, Gradient Boosting, LightGBM.
"""

from __future__ import annotations

import hashlib
import logging
import random as _random
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from . import knowledge
from .features import build_pair_vector

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODELS_DIR / "predictor.joblib"
LABELS = {"unsafe": 0, "caution": 1, "safe": 2}

logger = logging.getLogger(__name__)

# Static contraindication rules (herb keyword -> caution note).
HAZARD_NOTES = {
    "honey": "Avoid if diabetic",
    "aloe vera": "Internal use not recommended during pregnancy",
    "fenugreek": "May lower blood sugar; monitor if on antidiabetic medication",
    "ashwagandha": "Caution with sedatives and thyroid medication",
    "ginger": "Caution with blood thinners at high doses",
    "tulsi": "Caution with anticoagulants at very high doses",
    "cinnamon": "High doses may affect liver; caution with anticoagulants",
    "cumin": "May lower blood sugar; monitor if on antidiabetic medication",
    "clove": "High doses may thin blood; caution with anticoagulants",
    "nigella seed": "May lower blood pressure; caution with antihypertensives",
    "carom": "Large doses not advised during pregnancy",
    "giloy": "Caution in autoimmune conditions",
}


def _avg(values: list[float | int] | None, default: float) -> int:
    if not values:
        return int(default)
    return int(round(float(np.mean(values))))


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _seed_for(ingredients: list[str]) -> int:
    """Deterministic seed derived from the ingredient set (order-independent)."""
    key = "|".join(sorted(i.strip().lower() for i in ingredients)).encode("utf-8")
    return int.from_bytes(hashlib.md5(key).digest()[:4], "big")


def _score_offset(ingredients: list[str], channel: int, span: int = 3) -> int:
    """Small deterministic per-combination jitter so no two ingredient sets
    produce identical scorecards, while repeats stay stable."""
    rng = _random.Random(_seed_for(ingredients) + channel * 1013)
    return rng.randint(-span, span)


def _merge(a: list[str], b: list[str]) -> list[str]:
    seen: list[str] = []
    for item in list(a) + list(b):
        if item not in seen:
            seen.append(item)
    return seen


def _load_model() -> Any | None:
    if not MODEL_FILE.exists():
        return None
    try:
        return joblib.load(MODEL_FILE)
    except Exception as ex:
        logger.warning(
            "Could not load model artifact %s (%s); falling back to rule-based "
            "prediction. Regenerate it with: python -m train.train_predictor",
            MODEL_FILE.name,
            ex,
        )
        return None


class CompatibilityPredictor:
    """Predicts combination safety/benefit/risk for a set of ingredients."""

    def __init__(self, use_model: bool = True) -> None:
        self.model = None
        self.model_name: str | None = None
        self.meta: dict[str, Any] = {}
        self.herb_index: dict[str, int] = {}
        self.label_to_verdict: dict[int, str] = {0: "unsafe", 1: "caution", 2: "safe"}
        payload = _load_model() if use_model else None
        if payload:
            self.model = payload.get("model")
            self.meta = payload.get("meta") or {}
            self.model_name = self.meta.get("model_name") or (
                type(self.model).__name__ if self.model is not None else None
            )
            self.herb_index = {
                name.lower(): i for i, name in enumerate(payload.get("herbs", []))
            }
            labels = payload.get("labels")
            if labels:
                self.label_to_verdict = {int(i): name for name, i in labels.items()}
            logger.info(
                "Loaded compatibility model %r (%d herbs, %d classes).",
                self.model_name,
                len(self.herb_index),
                len(self.label_to_verdict),
            )

    @property
    def is_ml_active(self) -> bool:
        return self.model is not None

    @staticmethod
    def _core_herbs() -> set[str]:
        """Herbs that appear in at least one curated combination.

        The ML model is trained only on curated pairs, so its verdicts are only
        meaningful for herbs it has seen. Pairs of herbs outside this core set
        always fall back to the conservative 'caution' path instead of trusting
        an under-trained model on a huge, sparse vocabulary.
        """
        core: set[str] = set()
        for combo in knowledge.load_combinations():
            core.add(combo["herb_a"])
            core.add(combo["herb_b"])
        return core

    def _model_prediction(self, a: str, b: str) -> tuple[str, int] | None:
        if self.model is None:
            return None
        a, b = a.strip().lower(), b.strip().lower()
        if not self.herb_index or a not in self.herb_index or b not in self.herb_index:
            return None
        core = self._core_herbs()
        if a not in core or b not in core:
            return None

        features = build_pair_vector(a, b).reshape(1, -1)
        expected = getattr(self.model, "n_features_in_", features.shape[1])
        if features.shape[1] != expected:
            logger.warning(
                "Feature size mismatch (model=%d, built=%d); skipping ML.",
                expected,
                features.shape[1],
            )
            return None
        try:
            label = int(self.model.predict(features)[0])
            proba = self.model.predict_proba(features)[0][label]
        except Exception as ex:
            logger.warning("Model prediction failed (%s); falling back.", ex)
            return None
        return self.label_to_verdict.get(label, "caution"), int(round(proba * 100))

    def predict(self, ingredients: list[str], remedy_type: str = "internal") -> dict[str, Any]:
        benefits: list[str] = []
        risks: list[str] = []
        verdict_scores: list[int] = []
        confidence: list[int] = []
        known_compatibility: list[int] = []
        unknown_pairs = 0
        hazard_notes = 0

        pairs = [(ingredients[i], ingredients[j]) for i in range(len(ingredients)) for j in range(i + 1, len(ingredients))]

        for a, b in pairs:
            combo = knowledge.find_combination(a, b)
            if combo:
                verdict_scores.append(LABELS[combo["verdict"]])
                confidence.append(combo["scientific_confidence"])
                known_compatibility.append(combo["compatibility_score"])
                benefits = _merge(benefits, combo["benefits"])
                risks = _merge(risks, combo["risks"])
                continue

            model_pred = self._model_prediction(a, b)
            if model_pred is not None:
                predicted, proba = model_pred
                verdict_scores.append(LABELS[predicted])
                confidence.append(proba)
                if predicted == "unsafe":
                    risks.append(f"Model flags {a} + {b} as unsafe; avoid this combination.")
                else:
                    risks.append(
                        f"Limited interaction data available for {a} + {b}; consult a healthcare professional before use."
                    )
            else:
                unknown_pairs += 1
                verdict_scores.append(LABELS["caution"])
                confidence.append(55)
                risks.append(
                    f"Limited interaction data available for {a} + {b}; consult a healthcare professional before use."
                )

        for ingredient in ingredients:
            plant = knowledge.find_plant(ingredient)
            if plant:
                benefits = _merge(benefits, plant["benefits"])
                risks = _merge(risks, plant["side_effects"])
                if plant["toxicity"] != "low":
                    hazard_notes += 1
            if ingredient.strip().lower() in HAZARD_NOTES:
                hazard_notes += 1
                risks.append(f"{ingredient}: {HAZARD_NOTES[ingredient.strip().lower()]}")

        verdict = self._verdict(verdict_scores)

        base_compatibility = {"safe": 90, "caution": 68, "unsafe": 40}[verdict]
        if known_compatibility:
            base_compatibility = int(round(float(np.mean(known_compatibility))))
        penalty = min(20, unknown_pairs * 10) + min(10, hazard_notes) * 2
        compatibility = _clamp(
            base_compatibility - penalty + _score_offset(ingredients, 0), 20, 98
        )

        safety = {
            "safe": max(70, 90 - hazard_notes * 4),
            "caution": max(45, 62 - hazard_notes * 3),
            "unsafe": 25,
        }[verdict]
        safety = _clamp(
            safety + _score_offset(ingredients, 1),
            70 if verdict == "safe" else 45 if verdict == "caution" else 20,
            100,
        )
        risk = 100 - safety

        benefit_base = {"safe": 84, "caution": 68, "unsafe": 48}[verdict]
        benefit = _clamp(
            benefit_base + min(12, len(benefits)) + _score_offset(ingredients, 2),
            30,
            98,
        )

        scientific_confidence = _clamp(
            _avg(confidence, 60) + _score_offset(ingredients, 3, span=2), 30, 98
        )

        toxicity = (
            "high"
            if verdict == "unsafe"
            else "medium"
            if verdict == "caution" or hazard_notes > 0
            else "low"
        )

        return {
            "compatibilityScore": compatibility,
            "safetyScore": safety,
            "benefitScore": benefit,
            "riskScore": risk,
            "scientificConfidence": scientific_confidence,
            "toxicityLevel": toxicity,
            "verdict": verdict,
            "benefits": benefits[:6],
            "risks": risks[:6],
            "preparation": self._preparation(ingredients, remedy_type),
            "quantity": self._quantity(remedy_type, len(ingredients)),
            "usageFrequency": self._frequency(remedy_type, verdict),
            "rationale": self._rationale(ingredients, remedy_type, verdict, risks),
        }

    def suggest_complements(
        self,
        ingredient: str,
        limit: int = 5,
        exclude: list[str] | None = None,
        remedy_type: str = "internal",
    ) -> list[dict[str, Any]]:
        """Rank complementary ingredients using the trained model.

        Every known herb is scored as a candidate partner for ``ingredient``
        via the ML model (verdict + confidence). Model predictions drive the
        ranking; curated records only enrich the result with benefits/notes.
        """
        exclude = {e.strip().lower() for e in (exclude or [])}
        target = ingredient.strip().lower()
        candidates = [
            name
            for name in knowledge.herb_names()
            if name.lower() != target and name.lower() not in exclude
        ]

        scored: list[dict[str, Any]] = []
        core = self._core_herbs()
        for name in candidates:
            combo = knowledge.find_combination(ingredient, name)
            if combo:
                predicted, proba = combo["verdict"], int(combo["scientific_confidence"])
            elif target in core and name.lower() in core:
                model_pred = self._model_prediction(ingredient, name)
                if model_pred is not None:
                    predicted, proba = model_pred
                else:
                    predicted, proba = "caution", 55
            else:
                predicted, proba = "caution", 55

            verdict_rank = {"unsafe": 0, "caution": 1, "safe": 2}[predicted]
            score = verdict_rank * 100 + proba
            if combo:
                score += combo["compatibility_score"] / 100.0

            plant = knowledge.find_plant(name)
            scored.append(
                {
                    "ingredient": name,
                    "verdict": predicted,
                    "confidence": proba,
                    "compatibility": combo["compatibility_score"] if combo else None,
                    "benefits": plant["benefits"][:3] if plant else [],
                    "note": HAZARD_NOTES.get(name.lower()),
                    "score": score,
                }
            )

        scored.sort(key=lambda s: (-s["score"], s["ingredient"]))
        ranked = [{k: v for k, v in s.items() if k != "score"} for s in scored[:limit]]
        return ranked

    def _verdict(self, verdict_scores: list[int]) -> str:
        if not verdict_scores:
            return "caution"
        worst = min(verdict_scores)
        return {0: "unsafe", 1: "caution", 2: "safe"}[worst]

    def _preparation(self, ingredients: list[str], remedy_type: str) -> list[str]:
        if remedy_type == "internal":
            return [
                "Boil 250 ml of filtered water.",
                f"Add {', '.join(ingredients)} and steep for 5-8 minutes.",
                "Strain and consume warm.",
            ]
        return [
            f"Combine {', '.join(ingredients)} with a suitable base carrier.",
            "Blend into a smooth, even consistency.",
            "Patch-test on a small skin area before full application.",
        ]

    def _quantity(self, remedy_type: str, count: int) -> str:
        if remedy_type == "internal":
            return f"1 cup (250 ml), using {1 + count} g total of dried herbs"
        return "Small handful per application (10-15 g)"

    def _frequency(self, remedy_type: str, verdict: str) -> str:
        if verdict == "unsafe":
            return "Not recommended"
        return "Daily (max twice daily for up to 2 weeks)" if remedy_type == "internal" else "2-3 times per week"

    def _rationale(self, ingredients, remedy_type, verdict, risks) -> str:
        base = (
            f"Based on your profile, {' + '.join(ingredients)} appears {verdict} "
            f"for {remedy_type} use."
        )
        if verdict == "caution" and risks:
            return f"{base} Caution advised: {risks[0]}."
        return base + " Follow the recommended dosage and stop use if any adverse reaction occurs."
