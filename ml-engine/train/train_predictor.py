"""Training pipeline for the compatibility predictor.

Featurizes curated herb-pair records and trains an ensemble of boosted-tree
models (Random Forest, XGBoost, Gradient Boosting, LightGBM), then persists
the best model to models/predictor.joblib.

Usage:
    python -m train.train_predictor
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import cross_val_score, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import knowledge  # noqa: E402


def build_features(
    combos: list[dict], label_map: dict[str, int]
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    herbs = sorted(knowledge.herb_names())
    herb_index = {name.lower(): i for i, name in enumerate(herbs)}

    def one_hot(name: str) -> np.ndarray:
        vec = np.zeros(len(herbs))
        if name.lower() in herb_index:
            vec[herb_index[name.lower()]] = 1
        return vec

    rows = [
        np.concatenate([one_hot(combo["herb_a"]), one_hot(combo["herb_b"])])
        for combo in combos
    ]

    features = np.vstack(rows)
    targets = np.array([label_map[c["verdict"]] for c in combos])
    return features, targets, herbs


def main() -> None:
    combos = knowledge.load_combinations()
    if len(combos) < 10:
        print(f"Not enough combination records to train ({len(combos)}).")
        return

    classes = sorted({c["verdict"] for c in combos})
    label_map = {label: i for i, label in enumerate(classes)}

    x, y, herb_names = build_features(combos, label_map)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    models: list[tuple[str, object]] = [
        ("RandomForest", RandomForestClassifier(n_estimators=300, random_state=42)),
        ("GradientBoosting", GradientBoostingClassifier(n_estimators=200, random_state=42)),
    ]
    try:
        from xgboost import XGBClassifier

        models.append(("XGBoost", XGBClassifier(n_estimators=200, eval_metric="mlogloss")))
    except Exception as exc:  # noqa: BLE001
        print(f"XGBoost not available ({type(exc).__name__}); skipping.")
    try:
        from lightgbm import LGBMClassifier

        models.append(("LightGBM", LGBMClassifier(n_estimators=200, verbosity=-1)))
    except Exception as exc:  # noqa: BLE001
        print(f"LightGBM not available ({type(exc).__name__}); skipping.")

    n_splits = min(3, len(set(y)))
    if n_splits < 2 or any(int(np.sum(y == label)) < 2 for label in set(y)):
        n_splits = None

    best = None
    best_score = -1.0
    for name, model in models:
        try:
            if n_splits:
                score = cross_val_score(
                    model, x, y, cv=n_splits, scoring="f1_weighted", error_score="raise"
                ).mean()
            else:
                model.fit(x_train, y_train)
                score = f1_score(y_test, model.predict(x_test), average="weighted")
            print(f"{name}: f1={score:.3f}")
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: skipped ({type(exc).__name__}: {exc})")
            continue
        if score > best_score:
            best_score = score
            best = (name, model)

    if best is None:
        print("No model trained successfully.")
        return

    model = best[1]
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    print(
        f"Best model: {best[0]} | accuracy={accuracy_score(y_test, preds):.3f} "
        f"f1={f1_score(y_test, preds, average='weighted'):.3f}"
    )

    model_dir = Path(__file__).resolve().parent.parent / "models"
    model_dir.mkdir(exist_ok=True)
    joblib.dump(
        {"model": model, "herbs": herb_names, "labels": label_map},
        model_dir / "predictor.joblib",
    )
    print(f"Saved to {model_dir / 'predictor.joblib'}")


if __name__ == "__main__":
    main()
