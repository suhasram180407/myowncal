"""
Indian Food Nutrition - Full ML Pipeline
=========================================
Combines all 3 datasets, cleans them, engineers features,
splits 70/15/15, trains two models:
  1. Calorie Regressor  - predict Calories_per_100g from macros + features
  2. Category Classifier - predict food Category from nutrition profile

Run:
    python -m app.ml.pipeline
"""

import re
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    classification_report, accuracy_score,
)
import joblib

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "datasets" / "rawdata"
PROCESSED = BASE / "datasets" / "processed"
SPLIT = BASE / "datasets" / "split"
MODELS = BASE / "datasets" / "models"

for d in [PROCESSED, SPLIT, MODELS]:
    d.mkdir(parents=True, exist_ok=True)

# ── Category normalization map ─────────────────────────────────────────────────
# Unifies category names across all 3 datasets into 8 canonical labels
CATEGORY_MAP = {
    # Dataset 1 originals
    "non-veg": "Non-Veg",
    "veg": "Veg",
    "snacks": "Snacks",
    "bread": "Bread",
    "dessert": "Dessert",
    "lentils": "Lentils",
    "breakfast": "Breakfast",
    "condiment": "Condiment",
    # Dataset 2 originals
    "main dish": "Veg",
    "lentil dish": "Lentils",
    "staple": "Bread",
    "snack": "Snacks",
    "spice mix": "Condiment",
    "beverage": "Snacks",
    "soup": "Veg",
    "side dish": "Veg",
}


# ==============================================================================
# STEP 1 — LOAD & NORMALIZE EACH DATASET
# ==============================================================================

def parse_serving_grams(serving: str) -> float:
    """
    Extract gram weight from serving size strings like '1 bowl (200g)'.
    Returns the gram value so we can normalize to per-100g.
    """
    match = re.search(r"\((\d+(?:\.\d+)?)\s*(?:g|ml)\)", str(serving), re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 100.0  # fallback: assume 100g if unparseable


def load_dataset1() -> pd.DataFrame:
    """
    Sheet1.csv — 106 rows, already per 100g.
    Has: Category, Region, Spice_Level, Cooking_Method (richest metadata).
    """
    df = pd.read_csv(RAW / "indian_food_nutrition_calories - Sheet1.csv")
    df = df.rename(columns={
        "Food_Item": "food_name",
        "Calories_per_100g": "calories",
        "Protein_g": "protein",
        "Fat_g": "fat",
        "Carbs_g": "carbs",
        "Fiber_g": "fiber",
        "Sugar_g": "sugar",
        "Sodium_mg": "sodium",
        "Potassium_mg": "potassium",
        "Vitamin_C_mg": "vitamin_c",
        "Calcium_mg": "calcium",
        "Iron_mg": "iron",
        "Spice_Level": "spice_level",
        "Cooking_Method": "cooking_method",
        "Region": "region",
        "Category": "category",
    })
    df["source"] = "sheet1"
    print(f"  [DS1] Loaded {len(df)} rows from Sheet1")
    return df


def load_dataset2() -> pd.DataFrame:
    """
    nutrition_dataset.csv — 97 rows, per serving size.
    Normalizes all values to per-100g using the gram weight in 'Serving Size'.
    """
    df = pd.read_csv(RAW / "indian_food_nutrition_dataset.csv", on_bad_lines="skip")
    df = df.rename(columns={
        "Food Name": "food_name",
        "Calories (kcal)": "calories_raw",
        "Protein (g)": "protein_raw",
        "Carbohydrates (g)": "carbs_raw",
        "Fats (g)": "fat_raw",
        "Category": "category",
        "Dietary Preference": "dietary_pref",
        "Serving Size": "serving_size",
    })

    # Parse gram weight from serving size string
    df["serving_g"] = df["serving_size"].apply(parse_serving_grams)

    # Normalize all macro values to per-100g
    factor = 100.0 / df["serving_g"]
    df["calories"] = (df["calories_raw"] * factor).round(2)
    df["protein"]  = (df["protein_raw"]  * factor).round(2)
    df["carbs"]    = (df["carbs_raw"]    * factor).round(2)
    df["fat"]      = (df["fat_raw"]      * factor).round(2)

    # Map dietary preference to category where category is missing
    df["category"] = df["category"].fillna(df["dietary_pref"])
    df["source"] = "nutrition_dataset"
    print(f"  [DS2] Loaded {len(df)} rows from nutrition_dataset (normalized to per-100g)")
    return df[["food_name", "calories", "protein", "carbs", "fat", "category", "source"]]


def load_dataset3() -> pd.DataFrame:
    """
    Indian_Food_Nutrition_Processed.csv — 1014 rows, already per 100g.
    Largest dataset. No category column — will be inferred from calorie range.
    """
    df = pd.read_csv(RAW / "Indian_Food_Nutrition_Processed.csv")
    df = df.rename(columns={
        "Dish Name": "food_name",
        "Calories (kcal)": "calories",
        "Carbohydrates (g)": "carbs",
        "Protein (g)": "protein",
        "Fats (g)": "fat",
        "Free Sugar (g)": "sugar",
        "Fibre (g)": "fiber",
        "Sodium (mg)": "sodium",
        "Calcium (mg)": "calcium",
        "Iron (mg)": "iron",
        "Vitamin C (mg)": "vitamin_c",
    })
    df["source"] = "processed"
    # No category in this dataset — assign based on calorie density
    conditions = [
        df["calories"] <= 50,
        df["calories"] <= 150,
        df["calories"] <= 250,
        df["calories"] <= 400,
    ]
    choices = ["Snacks", "Veg", "Non-Veg", "Dessert"]
    df["category"] = np.select(conditions, choices, default="Non-Veg")
    print(f"  [DS3] Loaded {len(df)} rows from Processed")
    return df


# ==============================================================================
# STEP 2 — MERGE & CLEAN
# ==============================================================================

def merge_datasets(df1, df2, df3) -> pd.DataFrame:
    """
    Concatenate all three datasets on common columns.
    Fill missing columns with NaN — handled in cleaning step.
    """
    # Common columns present in all datasets
    common_cols = ["food_name", "calories", "protein", "carbs", "fat",
                   "fiber", "sugar", "sodium", "calcium", "iron",
                   "vitamin_c", "category", "source"]

    # Ensure all dataframes have all common columns
    for df in [df1, df2, df3]:
        for col in common_cols:
            if col not in df.columns:
                df[col] = np.nan

    merged = pd.concat(
        [df1[common_cols], df2[common_cols], df3[common_cols]],
        ignore_index=True,
    )
    print(f"\n  [MERGE] Combined shape: {merged.shape}")
    return merged


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
    1. Normalize food names (lowercase, strip)
    2. Normalize category labels
    3. Drop rows with missing calories/protein/carbs/fat
    4. Remove calorie outliers (< 5 or > 900 per 100g)
    5. Remove duplicates by food_name
    6. Fill remaining NaN numerics with column median
    """
    print("\n[CLEAN] Starting data cleaning...")
    original_len = len(df)

    # 1. Normalize food names
    df["food_name"] = df["food_name"].str.strip().str.lower()
    df["food_name"] = df["food_name"].str.replace(r"\s+", " ", regex=True)

    # 2. Normalize category labels to canonical set
    df["category"] = (
        df["category"]
        .str.strip()
        .str.lower()
        .map(lambda x: CATEGORY_MAP.get(str(x).lower(), x))
    )
    # Capitalize first letter
    df["category"] = df["category"].str.title()

    # 3. Drop rows missing core nutrition values
    core_cols = ["calories", "protein", "carbs", "fat"]
    df = df.dropna(subset=core_cols)
    print(f"  After dropping missing core values: {len(df)} rows")

    # 4. Remove calorie outliers
    df = df[(df["calories"] >= 5) & (df["calories"] <= 900)]
    print(f"  After calorie range filter (5-900): {len(df)} rows")

    # 5. Remove duplicate food names — keep the row with most non-null values
    df["_non_null_count"] = df.notna().sum(axis=1)
    df = df.sort_values("_non_null_count", ascending=False)
    df = df.drop_duplicates(subset=["food_name"], keep="first")
    df = df.drop(columns=["_non_null_count"])
    print(f"  After deduplication: {len(df)} rows")

    # 6. Fill remaining NaN numerics with column median
    numeric_cols = ["fiber", "sugar", "sodium", "calcium", "iron", "vitamin_c"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # 7. Merge rare categories (< 15 samples) into nearest parent
    # Lentils -> Veg, Condiment -> Snacks, Breakfast -> Veg, Bread -> Veg
    rare_map = {
        "Lentils": "Veg",
        "Condiment": "Snacks",
        "Breakfast": "Veg",
        "Bread": "Veg",
    }
    before = df["category"].value_counts().to_dict()
    df["category"] = df["category"].replace(rare_map)
    merged_count = sum(v for k, v in before.items() if k in rare_map)
    print(f"  Merged {merged_count} rows from rare categories into parent classes")
    print(f"  Final categories: {df['category'].value_counts().to_dict()}")

    # 8. Reset index
    df = df.reset_index(drop=True)
    print(f"  Removed {original_len - len(df)} rows total")
    print(f"  Final clean dataset: {len(df)} rows, {len(df.columns)} columns")
    return df


# ==============================================================================
# STEP 3 — FEATURE ENGINEERING
# ==============================================================================

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features that help the model:
    - macro_ratio_*: proportion of each macro in total macros
    - calorie_density_class: binned calorie level
    - protein_to_fat_ratio: useful for distinguishing food types
    """
    # Total macros (protein + carbs + fat) — avoid division by zero
    total_macros = df["protein"] + df["carbs"] + df["fat"]
    total_macros = total_macros.replace(0, np.nan)

    df["protein_ratio"] = (df["protein"] / total_macros).round(4)
    df["carb_ratio"]    = (df["carbs"]   / total_macros).round(4)
    df["fat_ratio"]     = (df["fat"]     / total_macros).round(4)

    # Protein-to-fat ratio — high = lean protein food, low = fatty food
    df["protein_fat_ratio"] = (df["protein"] / (df["fat"] + 0.1)).round(4)

    # Calorie density class (ordinal)
    df["calorie_class"] = pd.cut(
        df["calories"],
        bins=[0, 100, 200, 350, 900],
        labels=[0, 1, 2, 3],
    ).astype(float)

    # Fill any NaN from ratio calculations
    ratio_cols = ["protein_ratio", "carb_ratio", "fat_ratio", "protein_fat_ratio", "calorie_class"]
    for col in ratio_cols:
        df[col] = df[col].fillna(df[col].median())

    print(f"\n[FEATURES] Engineered {len(ratio_cols)} new features")
    return df


# ==============================================================================
# STEP 4 — ENCODE CATEGORICALS & SCALE
# ==============================================================================

def encode_and_scale(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Label-encode the 'category' column.
    Returns (encoded_df, encoders_dict) — encoders saved for inference.
    """
    encoders = {}

    # Encode category
    le = LabelEncoder()
    df["category_encoded"] = le.fit_transform(df["category"].astype(str))
    encoders["category"] = le
    print(f"\n[ENCODE] Category classes: {list(le.classes_)}")

    return df, encoders


# ==============================================================================
# STEP 5 — TRAIN / VALIDATION / TEST SPLIT  (70 / 15 / 15)
# ==============================================================================

def split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Stratified split on category_encoded so each split has balanced class distribution.
    70% train | 15% validation | 15% test
    """
    # First split: 70% train, 30% temp
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        shuffle=True,
        stratify=df["category_encoded"],
    )

    # Second split: 50% of temp = 15% val, 15% test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        shuffle=True,
        stratify=temp_df["category_encoded"],
    )

    print(f"\n[SPLIT] 70/15/15 stratified split:")
    print(f"  Train:      {len(train_df):>4} rows")
    print(f"  Validation: {len(val_df):>4} rows")
    print(f"  Test:       {len(test_df):>4} rows")

    # Save splits to CSV
    train_df.to_csv(SPLIT / "train.csv", index=False)
    val_df.to_csv(SPLIT / "validation.csv", index=False)
    test_df.to_csv(SPLIT / "test.csv", index=False)
    print(f"  Saved to: {SPLIT}")

    return train_df, val_df, test_df


# ==============================================================================
# STEP 6 — MODEL DEFINITIONS
# ==============================================================================

# Features used by both models
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


def build_calorie_regressor() -> GradientBoostingRegressor:
    """
    Gradient Boosting Regressor for calorie prediction.

    Why GBR over Linear Regression?
    - Food nutrition has non-linear relationships (e.g. fat contributes 9 kcal/g,
      protein/carbs contribute 4 kcal/g — but real foods have interactions)
    - GBR captures these non-linearities without manual feature engineering
    - Robust to outliers and missing values
    - Outperforms Random Forest on tabular regression tasks of this size
    """
    return GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.8,          # stochastic boosting — reduces overfitting
        max_features="sqrt",
        random_state=42,
        validation_fraction=0.1,
        n_iter_no_change=20,    # built-in early stopping
        tol=1e-4,
    )


def build_category_classifier() -> RandomForestClassifier:
    """
    Random Forest Classifier for food category prediction.

    Why Random Forest over SVM/LogReg?
    - Handles multi-class naturally (8 categories)
    - Provides feature importance scores
    - No need for feature scaling
    - Works well with 500-1000 samples
    - Less prone to overfitting than single decision tree
    """
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",  # handles class imbalance
        random_state=42,
        n_jobs=-1,
    )


# ==============================================================================
# STEP 7 — TRAIN & EVALUATE REGRESSOR
# ==============================================================================

def train_regressor(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    scaler: StandardScaler,
) -> GradientBoostingRegressor:
    """Train calorie regressor and evaluate on val + test sets."""
    print("\n" + "=" * 55)
    print("MODEL 1: Calorie Regressor (GradientBoostingRegressor)")
    print("=" * 55)

    # Prepare features
    X_train = scaler.fit_transform(train_df[REGRESSION_FEATURES])
    X_val   = scaler.transform(val_df[REGRESSION_FEATURES])
    X_test  = scaler.transform(test_df[REGRESSION_FEATURES])

    y_train = train_df["calories"].values
    y_val   = val_df["calories"].values
    y_test  = test_df["calories"].values

    # Train
    model = build_calorie_regressor()
    model.fit(X_train, y_train)
    print(f"  Trained in {model.n_estimators_} estimators (early stopping)")

    # Evaluate on validation set
    val_preds = model.predict(X_val)
    val_mae  = mean_absolute_error(y_val, val_preds)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_preds))
    val_r2   = r2_score(y_val, val_preds)

    print(f"\n  Validation Set:")
    print(f"    MAE:  {val_mae:.2f} kcal")
    print(f"    RMSE: {val_rmse:.2f} kcal")
    print(f"    R2:   {val_r2:.4f}")

    # Evaluate on test set
    test_preds = model.predict(X_test)
    test_mae  = mean_absolute_error(y_test, test_preds)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    test_r2   = r2_score(y_test, test_preds)

    print(f"\n  Test Set:")
    print(f"    MAE:  {test_mae:.2f} kcal")
    print(f"    RMSE: {test_rmse:.2f} kcal")
    print(f"    R2:   {test_r2:.4f}")

    # Feature importance
    importances = sorted(
        zip(REGRESSION_FEATURES, model.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )
    print(f"\n  Top 5 Feature Importances:")
    for feat, imp in importances[:5]:
        bar = "#" * int(imp * 50)
        print(f"    {feat:<22} {imp:.4f}  {bar}")

    # Sample predictions vs actuals
    print(f"\n  Sample Predictions (Test Set):")
    print(f"    {'Food':<35} {'Actual':>8} {'Predicted':>10} {'Error':>8}")
    print(f"    {'-'*65}")
    for i in range(min(8, len(test_df))):
        name = test_df.iloc[i]["food_name"][:33]
        actual = y_test[i]
        pred = test_preds[i]
        err = pred - actual
        print(f"    {name:<35} {actual:>8.1f} {pred:>10.1f} {err:>+8.1f}")

    return model, {
        "val_mae": val_mae, "val_rmse": val_rmse, "val_r2": val_r2,
        "test_mae": test_mae, "test_rmse": test_rmse, "test_r2": test_r2,
    }


# ==============================================================================
# STEP 8 — TRAIN & EVALUATE CLASSIFIER
# ==============================================================================

def train_classifier(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    label_encoder: LabelEncoder,
) -> RandomForestClassifier:
    """Train food category classifier and evaluate on val + test sets."""
    print("\n" + "=" * 55)
    print("MODEL 2: Category Classifier (RandomForestClassifier)")
    print("=" * 55)

    X_train = train_df[CLASSIFICATION_FEATURES].values
    X_val   = val_df[CLASSIFICATION_FEATURES].values
    X_test  = test_df[CLASSIFICATION_FEATURES].values

    y_train = train_df["category_encoded"].values
    y_val   = val_df["category_encoded"].values
    y_test  = test_df["category_encoded"].values

    # Train
    model = build_category_classifier()
    model.fit(X_train, y_train)

    # Validation
    val_preds = model.predict(X_val)
    val_acc = accuracy_score(y_val, val_preds)
    print(f"\n  Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")

    # Test
    test_preds = model.predict(X_test)
    test_acc = accuracy_score(y_test, test_preds)
    print(f"  Test Accuracy:       {test_acc:.4f} ({test_acc*100:.2f}%)")

    # Full classification report on test set
    class_names = list(label_encoder.classes_)
    report = classification_report(
        y_test, test_preds,
        target_names=class_names,
        digits=3,
        zero_division=0,
    )
    print(f"\n  Classification Report (Test Set):\n")
    for line in report.split("\n"):
        print(f"    {line}")

    # Feature importance
    importances = sorted(
        zip(CLASSIFICATION_FEATURES, model.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )
    print(f"\n  Top 5 Feature Importances:")
    for feat, imp in importances[:5]:
        bar = "#" * int(imp * 50)
        print(f"    {feat:<22} {imp:.4f}  {bar}")

    return model, {"val_acc": val_acc, "test_acc": test_acc}


# ==============================================================================
# STEP 9 — SAVE MODELS & ARTIFACTS
# ==============================================================================

def save_artifacts(
    regressor,
    classifier,
    scaler: StandardScaler,
    encoders: dict,
    reg_metrics: dict,
    clf_metrics: dict,
    df_clean: pd.DataFrame,
):
    """Save all models, scaler, encoders, and a metrics report."""
    joblib.dump(regressor,  MODELS / "calorie_regressor.pkl")
    joblib.dump(classifier, MODELS / "category_classifier.pkl")
    joblib.dump(scaler,     MODELS / "scaler.pkl")
    joblib.dump(encoders,   MODELS / "encoders.pkl")

    # Save label classes for inference
    label_map = {
        int(i): str(cls)
        for i, cls in enumerate(encoders["category"].classes_)
    }
    (MODELS / "label_map.json").write_text(json.dumps(label_map, indent=2))

    # Save feature column lists
    feature_info = {
        "regression_features": REGRESSION_FEATURES,
        "classification_features": CLASSIFICATION_FEATURES,
    }
    (MODELS / "feature_info.json").write_text(json.dumps(feature_info, indent=2))

    # Save metrics report
    metrics = {
        "calorie_regressor": reg_metrics,
        "category_classifier": clf_metrics,
        "dataset_size": len(df_clean),
    }
    (MODELS / "metrics.json").write_text(json.dumps(metrics, indent=2))

    print(f"\n[SAVED] All artifacts saved to: {MODELS}")
    print(f"  calorie_regressor.pkl")
    print(f"  category_classifier.pkl")
    print(f"  scaler.pkl")
    print(f"  encoders.pkl")
    print(f"  label_map.json")
    print(f"  feature_info.json")
    print(f"  metrics.json")


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def run_pipeline():
    print("=" * 55)
    print("Indian Food Nutrition - ML Pipeline")
    print("=" * 55)

    # Step 1: Load
    print("\n[LOAD] Loading all 3 datasets...")
    df1 = load_dataset1()
    df2 = load_dataset2()
    df3 = load_dataset3()

    # Step 2: Merge
    print("\n[MERGE] Combining datasets...")
    df = merge_datasets(df1, df2, df3)

    # Step 3: Clean
    df = clean_dataset(df)

    # Step 4: Feature engineering
    df = engineer_features(df)

    # Step 5: Encode
    df, encoders = encode_and_scale(df)

    # Save cleaned dataset
    df.to_csv(PROCESSED / "combined_clean.csv", index=False)
    print(f"\n[SAVED] Clean dataset: {PROCESSED / 'combined_clean.csv'}")

    # Step 6: Split
    train_df, val_df, test_df = split_data(df)

    # Step 7: Train regressor
    scaler = StandardScaler()
    regressor, reg_metrics = train_regressor(train_df, val_df, test_df, scaler)

    # Step 8: Train classifier
    classifier, clf_metrics = train_classifier(
        train_df, val_df, test_df, encoders["category"]
    )

    # Step 9: Save
    save_artifacts(regressor, classifier, scaler, encoders,
                   reg_metrics, clf_metrics, df)

    # Final summary
    print("\n" + "=" * 55)
    print("PIPELINE COMPLETE")
    print("=" * 55)
    print(f"  Dataset:          {len(df)} unique foods")
    print(f"  Train/Val/Test:   {len(train_df)}/{len(val_df)}/{len(test_df)}")
    print(f"  Calorie MAE:      {reg_metrics['test_mae']:.2f} kcal")
    print(f"  Calorie R2:       {reg_metrics['test_r2']:.4f}")
    print(f"  Category Acc:     {clf_metrics['test_acc']*100:.2f}%")
    print(f"  Models saved to:  {MODELS}")


if __name__ == "__main__":
    run_pipeline()
