"""Plant recognition module.

Stub that returns a deterministic identification from a small keyword set so
the API contract is testable. Swap the implementation with a trained
EfficientNet / ResNet50 / Vision Transformer checkpoint in the `models/`
directory and enable the TensorFlow/PyTorch extras in requirements.txt.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from . import knowledge

# Keyword -> herb name heuristics used only as a placeholder.
KEYWORD_MAP = {
    "green": "Tulsi",
    "purple": "Tulsi",
    "wavy": "Tulsi",
    "pinnate": "Neem",
    "serrated": "Neem",
    "sharp": "Neem",
    "long": "Aloe Vera",
    "spiky": "Aloe Vera",
    "fleshy": "Aloe Vera",
    "lanceolate": "Aloe Vera",
    "hairy": "Mint",
    "fuzzy": "Mint",
}


def recognize_pixels(pixels: np.ndarray) -> dict[str, Any]:
    """Placeholder recognizer. Returns the first matching keyword or unknown.

    Args:
        pixels: decoded image array of shape (height, width, channels).
    """
    height, width = pixels.shape[:2]
    aspect = width / max(height, 1)
    if aspect > 1.6:
        hint = "long"
    elif aspect < 0.7:
        hint = "long"
    else:
        hint = "green"

    herb = KEYWORD_MAP.get(hint, "Unknown")
    confidence = 0.62 if herb != "Unknown" else 0.31
    plant = knowledge.find_plant(herb)
    return {
        "identified": herb,
        "confidence": confidence,
        "medicinal_uses": plant["benefits"] if plant else [],
    }
