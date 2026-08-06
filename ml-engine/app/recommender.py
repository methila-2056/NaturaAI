"""Personalized Recommendation Engine.

Maps a user profile (age, gender, diseases, allergies, treatment type) to
candidate herbs, applies avoidance rules, and scores the compatibility of the
selected ingredient set for that individual.
"""

from __future__ import annotations

from typing import Any

from . import knowledge
from .predictor import CompatibilityPredictor


class RecommendationEngine:
    """Builds personalized remedy suggestions from profile + symptoms."""

    def __init__(self, predictor: CompatibilityPredictor | None = None) -> None:
        self.predictor = predictor or CompatibilityPredictor()

    def recommend(
        self,
        diseases: list[str],
        treatment_type: str = "internal",
        allergies: list[str] | None = None,
        age: int | None = None,
        gender: str | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        candidates: dict[str, float] = {}
        avoided = self._avoid_herbs(diseases)

        for disease_name in diseases or ["General Wellness"]:
            disease = knowledge.find_disease(disease_name)
            if not disease:
                continue
            for herb in disease["recommended_herbs"]:
                candidates[herb] = candidates.get(herb, 0.0) + 1.0
            avoided.update({herb: True for herb in disease["avoid_herbs"]})

        if not candidates:
            fallback = self._fallback_herbs(treatment_type, age, gender)
            candidates.update(fallback)

        usable = [
            name
            for name in candidates
            if name not in avoided and not self._allergen(name, allergies or [])
        ]
        usable.sort(key=lambda name: candidates[name], reverse=True)

        suggestions = usable[:limit]
        recommendations = []
        for herb in suggestions:
            analysis = self.predictor.predict([herb, self._pair_with(herb, treatment_type)], treatment_type)
            recommendations.append(
                {
                    "name": f"{herb} blend",
                    "ingredients": [herb, self._pair_with(herb, treatment_type)],
                    "treatmentType": treatment_type,
                    "verdict": analysis["verdict"],
                    "benefitScore": analysis["benefitScore"],
                    "benefits": analysis["benefits"],
                    "risks": analysis["risks"],
                }
            )
        return recommendations

    def _avoid_herbs(self, diseases: list[str]) -> dict[str, bool]:
        avoided: dict[str, bool] = {}
        for name in diseases:
            disease = knowledge.find_disease(name)
            if disease:
                for herb in disease["avoid_herbs"]:
                    avoided[herb] = True
        return avoided

    def _allergen(self, herb: str, allergies: list[str]) -> bool:
        herb_key = herb.lower()
        for allergy in allergies:
            key = allergy.lower()
            if key in herb_key or herb_key in key:
                return True
        return False

    def _fallback_herbs(self, treatment_type: str, age: int | None, gender: str | None) -> dict[str, float]:
        if treatment_type == "external":
            return {"Aloe Vera": 1.0, "Neem": 1.0, "Hibiscus": 1.0}
        if age is not None and age < 12:
            return {"Tulsi": 1.0, "Mint": 1.0}
        if gender == "female":
            return {"Ashwagandha": 1.0, "Amla": 1.0, "Fenugreek": 1.0}
        return {"Tulsi": 1.0, "Ginger": 1.0, "Ashwagandha": 1.0}

    def _pair_with(self, herb: str, treatment_type: str) -> str:
        external_pairs = {
            "Aloe Vera": "Neem",
            "Neem": "Aloe Vera",
            "Hibiscus": "Coconut Oil",
            "Turmeric": "Aloe Vera",
        }
        if treatment_type == "external":
            return external_pairs.get(herb, "Aloe Vera")
        internal_pairs = {
            "Tulsi": "Ginger",
            "Ginger": "Honey",
            "Honey": "Ginger",
            "Ashwagandha": "Brahmi",
            "Brahmi": "Ashwagandha",
            "Amla": "Hibiscus",
            "Fenugreek": "Ginger",
            "Mint": "Tulsi",
            "Lemon": "Ginger",
            "Green Tea": "Mint",
            "Moringa": "Ginger",
        }
        return internal_pairs.get(herb, "Tulsi")
