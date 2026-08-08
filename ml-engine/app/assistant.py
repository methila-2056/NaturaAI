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

GREETING_ANSWER = (
    "Namaste! I'm the NaturaAI herbal assistant. I can help with herb combinations, "
    "benefits, preparation methods, and safety. Try asking things like "
    "'Is Tulsi safe?' or 'Can I use Aloe Vera with Neem?' "
    + GENERIC_ANSWER
)

_THANKS_RE = re.compile(
    r"^\s*(thanks|thank\s*you|thanku|thx|bye|goodbye|ok|okay)\b", re.IGNORECASE
)
_GREETING_RE = re.compile(
    r"^\s*(hi+|hello+|hey+|namaste|good\s+(morning|afternoon|evening)|how\s+are\s+you)\b",
    re.IGNORECASE,
)


_DISEASE_KEYWORDS = {
    "Common Cold": ["common cold", "cold", "sore throat", "cough"],
    "Diabetes": ["diabet", "blood sugar", "blood glucose", "sugar patient"],
    "Hypertension": ["hypertension", "high blood pressure", "high bp", "blood pressure"],
    "Asthma": ["asthma", "wheez", "shortness of breath", "breathing"],
    "Thyroid": ["thyroid"],
    "PCOS": ["pcos", "polycystic"],
    "Skin Allergy": ["skin allergy", "skin allergies", "allerg"],
    "Eczema": ["eczema"],
    "Psoriasis": ["psoriasis"],
    "Acne": ["acne", "pimple"],
    "Hair Loss": ["hair loss", "hair fall", "thinning hair", "bald"],
    "Fever": ["fever", "body ache"],
    "Stress": ["stress", "anxious"],
    "Anxiety": ["anxiety", "restless", "racing thoughts"],
    "Insomnia": ["insomnia", "sleepless", "sleep"],
}

HERB_ALIASES = {
    "white pepper": "Black Pepper",
    "black pepper": "Black Pepper",
    "pepper": "Black Pepper",
    "kali mirch": "Black Pepper",
    "alovera": "Aloe Vera",
    "aloevera": "Aloe Vera",
    "aloe": "Aloe Vera",
    "tumeric": "Turmeric",
    "haldi": "Turmeric",
    "adrak": "Ginger",
    "methi": "Fenugreek",
    "fenugreek": "Fenugreek",
    "coconut": "Coconut Oil",
    "tea tree oil": "Tea Tree",
    "cinnamon": "Cinnamon",
    "dalchini": "Cinnamon",
    "jeera": "Cumin",
    "cumin": "Cumin",
    "dhania": "Coriander",
    "coriander": "Coriander",
    "cilantro": "Coriander",
    "laung": "Clove",
    "clove": "Clove",
    "elaichi": "Cardamom",
    "cardamom": "Cardamom",
    "saunf": "Fennel",
    "fennel": "Fennel",
    "ajwain": "Carom",
    "carom": "Carom",
    "kalonji": "Nigella Seed",
    "kadi patta": "Curry Leaves",
    "curry leaf": "Curry Leaves",
    "curry leaves": "Curry Leaves",
    "alsi": "Flaxseed",
    "flaxseed": "Flaxseed",
    "flax seed": "Flaxseed",
    "guduchi": "Giloy",
    "giloy": "Giloy",
    "bhringraj": "Bhringraj",
    "shatavari": "Shatavari",
    "amla": "Amla",
    "tulsi": "Tulsi",
}


def _matched_herbs(query: str) -> list[str]:
    lowered = query.lower()
    herbs = [herb for herb in knowledge.herb_names() if herb.lower() in lowered]
    for plant in knowledge.load_plants():
        english = (plant.get("english_name") or "").strip().lower()
        if (
            english
            and re.search(rf"\b{re.escape(english)}\b", lowered)
            and plant["name"] not in herbs
        ):
            herbs.append(plant["name"])
    for alias, name in HERB_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", lowered) and name not in herbs:
            herbs.append(name)
    return herbs


def _disease_from_query(query: str) -> dict[str, Any] | None:
    lowered = query.lower()
    for disease in knowledge.load_diseases():
        if disease["name"].lower() in lowered:
            return disease
    for disease_name, keywords in _DISEASE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            for disease in knowledge.load_diseases():
                if disease["name"].lower() == disease_name.lower():
                    return disease
    return None


def answer(query: str) -> dict[str, Any]:
    """Answer a natural-language question from the knowledge base.

    Returns a dict with 'answer' and the source grounding
    ('pair', 'herb', 'disease', 'greeting', 'thanks', 'llm' or 'generic').
    """
    herbs = _matched_herbs(query)
    disease = _disease_from_query(query)

    if len(herbs) >= 2:
        return _pair_answer(herbs, query)
    if herbs and disease:
        return _herb_for_disease_answer(herbs[0], disease, query)
    if herbs:
        return _herb_answer(herbs[0], query)
    if disease:
        return _disease_answer(disease, query)

    if _GREETING_RE.match(query):
        return {"answer": GREETING_ANSWER, "source": "greeting"}
    if _THANKS_RE.match(query):
        return {
            "answer": "You're welcome! Ask me about any herb or combination anytime. "
            + GENERIC_ANSWER,
            "source": "thanks",
        }

    llm_answer = _try_llm(query)
    if llm_answer:
        return {"answer": llm_answer, "source": "llm"}

    return {"answer": _unknown_help(query), "source": "generic"}


def _pair_answer(herbs: list[str], query: str) -> dict[str, Any]:
    a, b = herbs[0], herbs[1]
    combo = knowledge.find_combination(a, b)
    text = f"You asked about combining {a} and {b}. "
    if combo:
        text += (
            f"Based on curated data this combination is rated {combo['verdict']} "
            f"({combo['compatibility_score']}% compatibility, "
            f"{combo['scientific_confidence']}% scientific confidence). "
        )
        if combo["benefits"]:
            text += "Benefits: " + ", ".join(combo["benefits"]) + ". "
        if combo["risks"]:
            text += "Cautions: " + ", ".join(combo["risks"]) + ". "
    else:
        text += (
            "There is no curated interaction record for this pair yet, so treat it with "
            "caution and consult a healthcare professional before use. "
        )
    text += GENERIC_ANSWER
    return {"answer": text, "source": "pair", "herb": [a, b]}


def _herb_for_disease_answer(
    herb: str, disease: dict[str, Any], query: str
) -> dict[str, Any]:
    plant = knowledge.find_plant(herb)
    if not plant:
        return _herb_answer(herb, query)

    recommended = [h.lower() for h in disease["recommended_herbs"]]
    avoid = [h.lower() for h in disease["avoid_herbs"]]
    herb_key = herb.lower()

    if herb_key in avoid:
        guidance = (
            f"{herb} is generally AVOIDED for {disease['name']}; using it may be "
            f"unsafe for this condition."
        )
    elif herb_key in recommended:
        guidance = (
            f"{herb} is among the herbs NaturaAI recommends for {disease['name']}."
        )
    else:
        guidance = (
            f"no specific contraindication for {herb} is recorded for "
            f"{disease['name']}, so it is likely fine in normal amounts, but do "
            f"verify with a professional before use."
        )

    text = f"For {disease['name']}, {guidance} "
    text += _herb_answer(herb, query)["answer"]
    return {
        "answer": text,
        "source": "herb-disease",
        "herb": herb,
        "disease": disease["name"],
    }


def _herb_answer(herb: str, query: str) -> dict[str, Any]:
    plant = knowledge.find_plant(herb)
    if not plant:
        return {"answer": GENERIC_ANSWER, "source": "generic"}

    benefits = ", ".join(plant["benefits"])
    side_effects = ", ".join(plant["side_effects"]) or "no specific cautions recorded"
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


def _unknown_help(query: str) -> str:
    herbs = knowledge.herb_names()
    sample = ", ".join(herbs[:8])
    text = (
        f"I couldn't find \"{query.strip()}\" in my herbal knowledge base. I can answer "
        f"questions about herbs like {sample} and more. Try rephrasing, for example "
        f"'Is Tulsi safe?' or 'Can I use Aloe Vera with Neem?' "
    )
    return text + GENERIC_ANSWER


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
