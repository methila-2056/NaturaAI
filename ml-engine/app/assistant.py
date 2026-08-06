"""LLM Health Assistant.

A grounded, retrieval-first assistant. It answers from the knowledge base
first, then optionally delegates to a configured LLM provider
(OpenAI / HuggingFace / local Llama-Gemma-Mistral) for explanation.

Set LLM_API_KEY and LLM_MODEL to enable live LLM responses.
"""

from __future__ import annotations

import os
import re
from typing import Any

from . import knowledge

GENERIC_ANSWER = (
    "NaturaAI does not replace professional medical advice. Consult a qualified "
    "healthcare professional before consuming or applying any herbal remedy, "
    "especially with existing conditions, pregnancy, or prescription medications."
)


def _herb_from_query(query: str) -> str | None:
    lowered = query.lower()
    for herb in knowledge.herb_names():
        if herb.lower() in lowered:
            return herb
    return None


def _disease_from_query(query: str) -> dict[str, Any] | None:
    lowered = query.lower()
    for disease in knowledge.load_diseases():
        if disease["name"].lower() in lowered:
            return disease
    return None


def answer(query: str) -> dict[str, Any]:
    """Answer a natural-language question from the knowledge base.

    Returns a dict with 'answer' and the source grounding ('herb', 'disease').
    """
    herb = _herb_from_query(query)
    disease = _disease_from_query(query)

    if herb:
        return _herb_answer(herb, query)
    if disease:
        return _disease_answer(disease, query)

    llm_answer = _try_llm(query)
    if llm_answer:
        return {"answer": llm_answer, "source": "llm"}

    return {"answer": GENERIC_ANSWER, "source": "generic"}


def _herb_answer(herb: str, query: str) -> dict[str, Any]:
    plant = knowledge.find_plant(herb)
    if not plant:
        return {"answer": GENERIC_ANSWER, "source": "generic"}

    benefits = ", ".join(plant["benefits"])
    side_effects = ", ".join(plant["side_effects"]) or "none reported"
    text = (
        f"{plant['name']} ({plant['scientific_name']}) is traditionally used for: {benefits}. "
        f"Known side effects or cautions: {side_effects}. "
    )

    for other in knowledge.herb_names():
        combo = knowledge.find_combination(herb, other)
        if combo:
            text += (
                f"Combined with {other} it is rated {combo['verdict']} "
                f"({combo['compatibility_score']}% compatibility). "
            )

    text += GENERIC_ANSWER
    return {"answer": text, "source": "herb", "herb": herb}


def _disease_answer(disease: dict[str, Any], query: str) -> dict[str, Any]:
    recommended = ", ".join(disease["recommended_herbs"])
    avoid = ", ".join(disease["avoid_herbs"]) or "none"
    text = (
        f"For {disease['name']} (symptoms: {', '.join(disease['symptoms'])}), NaturaAI "
        f"suggests: {recommended}. Avoid: {avoid}. "
    )
    text += GENERIC_ANSWER
    return {"answer": text, "source": "disease", "disease": disease["name"]}


def _try_llm(query: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    try:
        from .llm_client import ask_llm

        return ask_llm(query)
    except Exception:
        return None


def extract_pair(query: str) -> tuple[str, str] | None:
    """Best-effort extraction of two herbs from a question like
    'Can I use Aloe Vera with Neem?'"""
    herbs = [herb for herb in knowledge.herb_names() if re.search(rf"\b{re.escape(herb)}\b", query, re.IGNORECASE)]
    herbs = [h for h in herbs if h.lower() in {"tulsi", "neem", "aloe vera", "turmeric", "honey", "ginger", "hibiscus"}]
    if len(herbs) >= 2:
        return herbs[0], herbs[1]
    return None
