"""
Inference module for the trained Indian Food Nutrition models.

Loads:
  - calorie_regressor.pkl   (GradientBoostingRegressor)
  - category_classifier.pkl (RandomForestClassifier)
  - scaler.pkl              (StandardScaler)
  - encoders.pkl            (LabelEncoders)
  - label_map.json          (index -> category name)

Exposes:
  predict_calories(nutrition_dict)  -> float
  predict_category(nutrition_dict)  -> str
  predict_full(nutrition_dict)      -> dict
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from functools import lru_cache

from loguru import logger
import sklearn
import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent / "datasets" / "models"

REGRESSION_FEATURES = [
    "protein", "carbs", "fat", "fiber", "sugar",
    "sodium", "calcium", "iron", "vitamin_c",
    "protein_ratio", "carb_ratio", "fat_ratio",
    "protein_fat_ratio",
]

CLASSIFICATION_FEATURES = [
    "calories", "protein", "carbs", "fat", "fiber", "sugar",
    "sodium", "calcium", "iron", "vitamin_c",
    "protein_ratio", "carb_ratio", "fat_ratio",
    "protein_fat_ratio", "calorie_class",
]


REQUIRED_ARTIFACTS = [
    "calorie_regressor.pkl",
    "category_classifier.pkl",
    "scaler.pkl",
    "encoders.pkl",
    "label_map.json",
]


@lru_cache(maxsize=1)
def _load_artifacts():
    """Load all model artifacts once and cache them."""
    logger.info("ML inference startup: sklearn {}, artifacts path {}", sklearn.__version__, MODELS_DIR)

    missing = [name for name in REQUIRED_ARTIFACTS if not (MODELS_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing ML artifact files at {MODELS_DIR}: {missing}. Run: python -m app.ml.pipeline"
        )

    artifacts = {
        "regressor":  joblib.load(MODELS_DIR / "calorie_regressor.pkl"),
        "classifier": joblib.load(MODELS_DIR / "category_classifier.pkl"),
        "scaler":     joblib.load(MODELS_DIR / "scaler.pkl"),
        "encoders":   joblib.load(MODELS_DIR / "encoders.pkl"),
        "label_map":  json.loads((MODELS_DIR / "label_map.json").read_text()),
    }
    logger.info("ML inference artifacts loaded: {}", list(artifacts.keys()))
    return artifacts


def _build_feature_vector(nutrition: dict) -> dict:
    """
    Compute derived features from raw nutrition values.
    All values assumed to be per 100g.
    Missing values default to 0.
    """
    protein = float(nutrition.get("protein", 0) or 0)
    carbs   = float(nutrition.get("carbs",   0) or 0)
    fat     = float(nutrition.get("fat",     0) or 0)
    fiber   = float(nutrition.get("fiber",   0) or 0)
    sugar   = float(nutrition.get("sugar",   0) or 0)
    sodium  = float(nutrition.get("sodium",  0) or 0)
    calcium = float(nutrition.get("calcium", 0) or 0)
    iron    = float(nutrition.get("iron",    0) or 0)
    vit_c   = float(nutrition.get("vitamin_c", 0) or 0)

    total_macros = protein + carbs + fat or 1.0  # avoid division by zero
    protein_ratio = protein / total_macros
    carb_ratio    = carbs   / total_macros
    fat_ratio     = fat     / total_macros
    protein_fat_ratio = protein / (fat + 0.1)

    return {
        "protein": protein, "carbs": carbs, "fat": fat,
        "fiber": fiber, "sugar": sugar, "sodium": sodium,
        "calcium": calcium, "iron": iron, "vitamin_c": vit_c,
        "protein_ratio": protein_ratio,
        "carb_ratio": carb_ratio,
        "fat_ratio": fat_ratio,
        "protein_fat_ratio": protein_fat_ratio,
    }


def predict_calories(nutrition: dict) -> float:
    """
    Predict calories per 100g from macro/micronutrient values.

    Args:
        nutrition: dict with keys — protein, carbs, fat, fiber, sugar,
                   sodium, calcium, iron, vitamin_c (all per 100g)
    Returns:
        Predicted calories (kcal per 100g)
    """
    artifacts = _load_artifacts()
    features = _build_feature_vector(nutrition)
    X_reg = pd.DataFrame([[features[f] for f in REGRESSION_FEATURES]], columns=REGRESSION_FEATURES)
    X_scaled = artifacts["scaler"].transform(X_reg)
    prediction = artifacts["regressor"].predict(X_scaled)[0]
    return round(float(prediction), 2)


def predict_category(nutrition: dict, calories: float = None) -> str:
    """
    Predict food category from nutrition profile.

    Args:
        nutrition: dict with macro/micronutrient values per 100g
        calories: known calorie value (if available); if None, it is predicted first
    Returns:
        Category string e.g. 'Veg', 'Non-Veg', 'Dessert', 'Snacks'
    """
    artifacts = _load_artifacts()
    features = _build_feature_vector(nutrition)

    # Use provided calories or predict them
    cal = calories if calories is not None else predict_calories(nutrition)

    # Calorie class (ordinal bin)
    if cal <= 100:
        calorie_class = 0.0
    elif cal <= 200:
        calorie_class = 1.0
    elif cal <= 350:
        calorie_class = 2.0
    else:
        calorie_class = 3.0

    X = np.array([[
        cal,
        *[features[f] for f in CLASSIFICATION_FEATURES[1:-1]],  # skip calories + calorie_class
        calorie_class,
    ]])

    pred_idx = artifacts["classifier"].predict(X)[0]
    label_map = artifacts["label_map"]
    return label_map[str(int(pred_idx))]


def predict_full(nutrition: dict) -> dict:
    """
    Run both models and return a combined prediction result.

    Args:
        nutrition: dict with macro/micronutrient values per 100g

    Returns:
        {
            "predicted_calories": float,
            "predicted_category": str,
            "category_probabilities": {category: probability},
            "input_features": dict,
        }
    """
    artifacts = _load_artifacts()
    features = _build_feature_vector(nutrition)

    # Calorie prediction
    X_reg = pd.DataFrame([[features[f] for f in REGRESSION_FEATURES]], columns=REGRESSION_FEATURES)
    X_scaled = artifacts["scaler"].transform(X_reg)
    predicted_calories = round(float(artifacts["regressor"].predict(X_scaled)[0]), 2)

    # Category prediction with probabilities
    calorie_class = min(3.0, max(0.0, (predicted_calories - 1) // 100))
    X_clf = np.array([[
        predicted_calories,
        *[features[f] for f in CLASSIFICATION_FEATURES[1:-1]],
        calorie_class,
    ]])

    pred_idx = artifacts["classifier"].predict(X_clf)[0]
    pred_probs = artifacts["classifier"].predict_proba(X_clf)[0]

    label_map = artifacts["label_map"]
    category_probs = {
        label_map[str(i)]: round(float(p), 4)
        for i, p in enumerate(pred_probs)
    }

    return {
        "predicted_calories": predicted_calories,
        "predicted_category": label_map[str(int(pred_idx))],
        "category_probabilities": category_probs,
        "input_features": {k: round(v, 4) for k, v in features.items()},
    }
