from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import knowledge  # noqa: E402
from app.assistant import (  # noqa: E402
    GENERIC_ANSWER,
    GREETING_ANSWER,
    answer,
)


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def _ensure_data() -> None:
    assert knowledge.load_plants(), "plants.csv missing or empty"


def test_greeting_gets_friendly_response() -> None:
    for query in ("hii", "hello", "how are you", "namaste"):
        result = answer(query)
        assert result["source"] == "greeting"
        assert result["answer"] == GREETING_ANSWER


def test_thanks_gets_response() -> None:
    result = answer("thank you")
    assert result["source"] == "thanks"
    assert "You're welcome" in result["answer"]


def test_unknown_herb_gets_helpful_fallback() -> None:
    result = answer("lavender for skin glow")
    assert result["source"] == "generic"
    assert "lavender" in result["answer"]
    assert "I couldn't find" in result["answer"]
    assert GENERIC_ANSWER in result["answer"]


def test_pepper_matches_black_pepper() -> None:
    result = answer("pepper for face pack")
    assert result["source"] == "herb"
    assert result["herb"] == "Black Pepper"
    assert "Boosts nutrient absorption" in result["answer"]


def test_white_pepper_matches_black_pepper() -> None:
    result = answer("white pepper for digestion")
    assert result["source"] == "herb"
    assert result["herb"] == "Black Pepper"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("jeera for bloating", "Cumin"),
        ("haldi benefits", "Turmeric"),
        ("adrak benefits", "Ginger"),
        ("is methi good for hair", "Fenugreek"),
        ("dhania for digestion", "Coriander"),
        ("laung for toothache", "Clove"),
        ("elaichi for breath", "Cardamom"),
        ("saunf after meals", "Fennel"),
        ("ajwain for gas", "Carom"),
        ("kalonji seeds", "Nigella Seed"),
        ("kadi patta for hair", "Curry Leaves"),
        ("guduchi immunity", "Giloy"),
        ("shatavari benefits", "Shatavari"),
    ],
)
def test_vernacular_aliases(query: str, expected: str) -> None:
    result = answer(query)
    assert result["source"] == "herb"
    assert result["herb"] == expected


def test_short_alias_does_not_false_match() -> None:
    result = answer("until we meet again")
    assert result["source"] == "generic"


def test_new_large_catalog_herb_answerable() -> None:
    result = answer("Arjuna for heart health")
    assert result["source"] == "herb"
    assert result["herb"] == "Arjuna"
    assert "Supports heart health" in result["answer"]


def test_english_name_matches_herb() -> None:
    result = answer("holy basil benefits")
    assert result["source"] == "herb"
    assert result["herb"] == "Tulsi"


def test_english_phrase_does_not_false_match() -> None:
    result = answer("indian herbs for skin glow")
    assert result["source"] == "generic"


def test_toxic_herb_warns_in_answer() -> None:
    result = answer("What is Dhattura?")
    assert result["source"] == "herb"
    assert result["herb"] == "Dhattura"
    assert "toxic" in result["answer"].lower()


def test_herb_with_disease_gets_disease_context() -> None:
    result = answer("Is Turmeric safe for diabetics?")
    assert result["source"] == "herb-disease"
    assert result["disease"] == "Diabetes"
    assert "Diabetes" in result["answer"]
    assert "no specific contraindication" in result["answer"]


def test_avoided_herb_for_disease_is_warned() -> None:
    result = answer("Is Honey safe for diabetes?")
    assert result["source"] == "herb-disease"
    assert result["disease"] == "Diabetes"
    assert "AVOIDED" in result["answer"]


def test_recommended_herb_for_disease() -> None:
    result = answer("Is Fenugreek good for diabetes?")
    assert result["source"] == "herb-disease"
    assert result["disease"] == "Diabetes"
    assert "recommends" in result["answer"]


def test_single_herb_answer() -> None:
    result = answer("Can Hibiscus improve hair growth?")
    assert result["source"] == "herb"
    assert result["herb"] == "Hibiscus"
    assert "Promotes hair growth" in result["answer"]
    assert GENERIC_ANSWER in result["answer"]


def test_pair_answer_is_specific() -> None:
    result = answer("Can I use Aloe Vera with Neem?")
    assert result["source"] == "pair"
    assert result["herb"] == ["Neem", "Aloe Vera"]
    assert "Neem and Aloe Vera" in result["answer"]
    assert "safe" in result["answer"]
    assert GENERIC_ANSWER in result["answer"]


def test_pair_answer_without_record_advises_caution() -> None:
    result = answer("Can I use Moringa with Rose?")
    assert result["source"] == "pair"
    assert "no curated interaction record" in result["answer"]
