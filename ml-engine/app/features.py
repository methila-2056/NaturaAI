"""Shared featurization for the compatibility predictor.

Both the training pipeline (train/train_predictor.py) and the runtime
predictor (app/predictor.py) build herb-pair feature vectors through this
module, so the training and inference layouts can never drift apart.

Feature vector layout (per herb):
    - one-hot over the sorted herb vocabulary (from data/plants.csv)
    - one-hot over the toxicity level (low | medium | high)
    - one-hot over the usage mode (internal | external)

A pair is represented by concatenating the two per-herb blocks.
"""

from __future__ import annotations

import numpy as np

from . import knowledge

TOXICITY_LEVELS = ["low", "medium", "high"]
USAGE_LEVELS = ["internal", "external"]


def herb_vocab() -> list[str]:
    """Sorted, lowercased herb names used for the one-hot encoding."""
    return sorted(name.lower() for name in knowledge.herb_names())


def _per_herb_block(name: str) -> np.ndarray:
    herbs = herb_vocab()
    herb_index = {h: i for i, h in enumerate(herbs)}
    toxicity_index = {level: i for i, level in enumerate(TOXICITY_LEVELS)}
    usage_index = {mode: i for i, mode in enumerate(USAGE_LEVELS)}

    block = np.zeros(len(herbs) + len(TOXICITY_LEVELS) + len(USAGE_LEVELS))
    idx = herb_index.get(name.strip().lower())
    if idx is not None:
        block[idx] = 1.0

    plant = knowledge.find_plant(name)
    if plant:
        toxicity = plant["toxicity"].strip().lower()
        if toxicity in toxicity_index:
            block[len(herbs) + toxicity_index[toxicity]] = 1.0
        usage = plant["usage"].strip().lower()
        if usage in usage_index:
            block[len(herbs) + len(TOXICITY_LEVELS) + usage_index[usage]] = 1.0
    return block


def build_pair_vector(a: str, b: str) -> np.ndarray:
    """Build the concatenated feature vector for the (unordered) pair a, b."""
    return np.concatenate([_per_herb_block(a), _per_herb_block(b)])
