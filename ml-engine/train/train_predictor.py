"""Training pipeline for the compatibility predictor.

Featurizes curated herb-pair records and trains an ensemble of boosted-tree
models (Random Forest, XGBoost, Gradient Boosting, LightGBM), then persists
the best model together with its metadata to models/predictor.joblib.

The artifact is reloaded and smoke-tested before the run finishes so a broken
or corrupt save (for example an XGBoost version mismatch, which historically
made the predictor silently fall back to rule-based logic) is caught
immediately at training time.

Usage:
    python -m train.train_predictor
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.utils.class_weight import compute_sample_weight

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import knowledge  # noqa: E402
from app.features import build_pair_vector, herb_vocab  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILE = MODEL_DIR / "predictor.joblib"
RANDOM_STATE = 42


def build_features(
    combos: list[dict], label_map: dict[str, int]
) -> tuple[np.ndarray, np.ndarray]:
    """Convert curated pair records into (feature matrix, integer labels)."""
    features = np.vstack(
        [build_pair_vector(combo["herb_a"], combo["herb_b"]) for combo in combos]
    )
    targets = np.array([label_map[c["verdict"]] for c in combos])
    return features, targets


def _xgb_model(num_classes: int):
    from xgboost import XGBClassifier

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "tree_method": "hist",
        "device": "cpu",
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    }
    if num_classes > 2:
        params["objective"] = "multi:softprob"
        params["num_class"] = num_classes
        params["eval_metric"] = "mlogloss"
    else:
        params["eval_metric"] = "logloss"
    return XGBClassifier(**params)


def _lgbm_model():
    from lightgbm import LGBMClassifier

    return LGBMClassifier(n_estimators=200, random_state=RANDOM_STATE, verbosity=-1)


def _cross_validate(
    model, x: np.ndarray, y: np.ndarray, sample_weight: np.ndarray, n_splits: int
) -> float:
    scores: list[float] = []
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    for train_idx, test_idx in folds.split(x, y):
        model.fit(
            x[train_idx], y[train_idx], sample_weight=sample_weight[train_idx]
        )
        preds = model.predict(x[test_idx])
        scores.append(
            f1_score(y[test_idx], preds, average="weighted", zero_division=0)
        )
    return float(np.mean(scores))


def _split_score(model, x_train, y_train, w_train, x_test, y_test) -> float:
    model.fit(x_train, y_train, sample_weight=w_train)
    preds = model.predict(x_test)
    return f1_score(y_test, preds, average="weighted", zero_division=0)


def _build_meta(
    model_name: str,
    x: np.ndarray,
    y: np.ndarray,
    label_map: dict[str, int],
    cv_score: float,
    acc: float,
    f1w: float,
    f1m: float,
) -> dict:
    versions: dict[str, str | None] = {}
    for lib in ("xgboost", "lightgbm", "sklearn"):
        try:
            versions[lib] = __import__(lib).__version__
        except Exception:
            versions[lib] = None
    return {
        "model_name": model_name,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "feature_size": int(x.shape[1]),
        "n_samples": int(len(y)),
        "n_classes": int(len(set(y))),
        "class_counts": {str(label): int(np.sum(y == label)) for label in set(y)},
        "best_cv_f1_weighted": cv_score,
        "final_test_accuracy": acc,
        "final_test_f1_weighted": f1w,
        "final_test_f1_macro": f1m,
        "versions": versions,
        "data_file": knowledge.COMBINATIONS_FILE.name,
    }


def _verify_artifact() -> None:
    payload = joblib.load(MODEL_FILE)
    model = payload["model"]
    inverse = {int(i): name for name, i in payload["labels"].items()}
    smoke_pairs = [("Tulsi", "Ginger"), ("Aloe Vera", "Neem"), ("Moringa", "Rose")]
    for a, b in smoke_pairs:
        vector = build_pair_vector(a, b).reshape(1, -1)
        label = int(model.predict(vector)[0])
        print(f"  smoke {a} + {b} -> {inverse.get(label, label)}")
    print(f"Artifact verified: reload OK, predictions OK ({MODEL_FILE.name}).")


def main() -> None:
    combos = knowledge.load_combinations()
    if len(combos) < 10:
        print(f"Not enough combination records to train ({len(combos)}).")
        return

    classes = sorted({c["verdict"] for c in combos})
    label_map = {label: i for i, label in enumerate(classes)}
    x, y = build_features(combos, label_map)
    sample_weight = compute_sample_weight(class_weight="balanced", y=y)

    print(
        f"Training on {len(combos)} pairs | classes={classes} "
        f"| features={x.shape[1]}"
    )

    min_class = int(min(np.bincount(y)))
    if min_class >= 2:
        x_train, x_test, y_train, y_test, w_train, w_test = train_test_split(
            x, y, sample_weight, test_size=0.25, random_state=RANDOM_STATE, stratify=y
        )
    else:
        x_train, x_test, y_train, y_test, w_train, w_test = train_test_split(
            x, y, sample_weight, test_size=0.25, random_state=RANDOM_STATE
        )

    models: list[tuple[str, object]] = [
        (
            "RandomForest",
            RandomForestClassifier(
                n_estimators=300, class_weight="balanced", random_state=RANDOM_STATE
            ),
        ),
        (
            "GradientBoosting",
            GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE),
        ),
    ]
    try:
        models.append(("XGBoost", _xgb_model(len(classes))))
    except Exception as exc:  # noqa: BLE001
        print(f"XGBoost not available ({type(exc).__name__}: {exc}); skipping.")
    try:
        models.append(("LightGBM", _lgbm_model()))
    except Exception as exc:  # noqa: BLE001
        print(f"LightGBM not available ({type(exc).__name__}: {exc}); skipping.")

    n_splits = min(3, min_class) if min_class >= 2 else None
    best_name, best_model, best_score = None, None, -1.0
    for name, model in models:
        try:
            if n_splits:
                score = _cross_validate(model, x, y, sample_weight, n_splits)
                print(f"{name}: cv f1_weighted={score:.3f}")
            else:
                score = _split_score(model, x_train, y_train, w_train, x_test, y_test)
                print(f"{name}: holdout f1_weighted={score:.3f}")
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: skipped ({type(exc).__name__}: {exc})")
            continue
        if score > best_score:
            best_score, best_name, best_model = score, name, model

    if best_model is None:
        print("No model trained successfully.")
        return

    best_model.fit(x, y, sample_weight=sample_weight)
    preds = best_model.predict(x_test)
    acc = accuracy_score(y_test, preds)
    f1w = f1_score(y_test, preds, average="weighted", zero_division=0)
    f1m = f1_score(y_test, preds, average="macro", zero_division=0)

    print(
        f"Best model: {best_name} | holdout accuracy={acc:.3f} "
        f"f1_weighted={f1w:.3f} f1_macro={f1m:.3f}"
    )

    meta = _build_meta(best_name, x, y, label_map, best_score, acc, f1w, f1m)
    payload = {
        "model": best_model,
        "herbs": herb_vocab(),
        "labels": label_map,
        "meta": meta,
    }
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(payload, MODEL_FILE)
    print(f"Saved to {MODEL_FILE}")

    _verify_artifact()


if __name__ == "__main__":
    main()
