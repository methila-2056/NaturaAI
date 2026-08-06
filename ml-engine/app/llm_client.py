"""Optional LLM client.

Enabled when OPENAI_API_KEY is set. For local models (Llama 4, Gemma,
Mistral) run a compatible OpenAI-style endpoint and point OPENAI_BASE_URL
at it, e.g. via Ollama or vLLM.
"""

from __future__ import annotations

import os

from .assistant import GENERIC_ANSWER


def ask_llm(query: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NaturaAI, a cautious herbal-medicine assistant. "
                        "Answer from scientific herbal literature. Always end with a "
                        "safety disclaimer. Never give definitive medical advice."
                    ),
                },
                {"role": "user", "content": query},
            ],
            max_tokens=300,
        )
        answer = response.choices[0].message.content
        return (answer or GENERIC_ANSWER) + " " + GENERIC_ANSWER
    except ImportError:
        return GENERIC_ANSWER
