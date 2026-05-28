"""
Food dataset + search + ML fallback + quantity scaling.

Single source of truth: combined_clean.csv + trained ML models.
Loaded once at application startup.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger
from rapidfuzz import fuzz, process

DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "datasets" / "processed" / "combined_clean.csv"
)

FUZZY_THRESHOLD = 55
HIGH_CONFIDENCE = 85
SEARCH_LIMIT = 10

# (regex, grams per serving, serving_size label, quantity_unit hint)
SERVING_RULES: list[tuple[str, float, str, str]] = [
    (r"\bidli\b", 40.0, "1 piece", "piece"),
    (r"\bdosa\b", 80.0, "1 piece", "piece"),
    (r"\buttapam\b", 90.0, "1 piece", "piece"),
    (r"\bvada\b", 50.0, "1 piece", "piece"),
    (r"\bsamosa\b", 60.0, "1 piece", "piece"),
    (r"\bkachori\b", 55.0, "1 piece", "piece"),
    (r"\bpuri\b", 30.0, "1 piece", "piece"),
    (r"\bchapati\b|\broti\b|\bphulka\b", 35.0, "1 piece", "piece"),
    (r"\bnaan\b|\bparatha\b", 80.0, "1 piece", "piece"),
    (r"\bpizza\b", 100.0, "1 slice", "slice"),
    (r"\bbiryani\b|\bbiriyani\b", 250.0, "1 plate", "plate"),
    (r"\bbowl\b|khichdi|upma|poha|dal\b|curry\b|sambar\b|rasam\b", 200.0, "1 bowl", "bowl"),
    (r"\bbanana\b", 120.0, "1 banana", "piece"),
    (r"\blassi\b|buttermilk|chai\b|tea\b|coffee\b", 200.0, "1 cup", "cup"),
    (r"\brice\b", 150.0, "1 bowl", "bowl"),
    (r"\bgulab|rasgulla|ladoo\b|jalebi\b", 40.0, "1 piece", "piece"),
]

DEFAULT_SERVING_GRAMS = 100.0
DEFAULT_SERVING_LABEL = "1 serving"
DEFAULT_QUANTITY_UNIT = "serving"


class FoodService:
    """In-memory food catalog with fuzzy search and ML fallback."""

    def __init__(self) -> None:
        self._loaded = False
        self._entries: list[dict[str, Any]] = []
        self._names: list[str] = []
        self._by_name: dict[str, dict[str, Any]] = {}
        self._ml_ready = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def food_count(self) -> int:
        return len(self._entries)

    @property
    def ml_ready(self) -> bool:
        return self._ml_ready

    def initialize(self) -> None:
        """Load dataset and ML artifacts once at startup."""
        if self._loaded and self._ml_ready:
            return

        if not self._loaded:
            if not DATASET_PATH.exists():
                raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

            df = pd.read_csv(DATASET_PATH, encoding="utf-8")
            df.columns = [str(c).strip().lower() for c in df.columns]

            required = {"food_name", "calories", "protein", "carbs", "fat", "category"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"Dataset missing columns: {missing}")

            df["food_name"] = df["food_name"].astype(str).str.strip()
            df = df[df["food_name"].str.len() > 0]
            df = df.drop_duplicates(subset=["food_name"], keep="first")

            for col in ("calories", "protein", "carbs", "fat", "fiber", "sugar", "sodium"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            entries: list[dict[str, Any]] = []
            for _, row in df.iterrows():
                entry = self._row_to_entry(row)
                if entry["calories"] is not None:
                    entries.append(entry)

            self._entries = entries
            self._names = [e["food_name"] for e in entries]
            self._by_name = {e["food_name"].lower(): e for e in entries}
            self._loaded = True

        try:
            import app.ml.inference as inference

            logger.info("Loading ML artifacts from {}", inference.MODELS_DIR)
            inference._load_artifacts()
            self._ml_ready = True
            logger.info("ML artifacts loaded successfully")
        except Exception as exc:
            self._ml_ready = False
            logger.exception("ML artifact loading failed: {}", exc)

    def _row_to_entry(self, row: pd.Series) -> dict[str, Any]:
        food_name = str(row["food_name"]).strip()
        display = food_name.title()
        grams, serving_label, qty_unit = infer_serving(food_name)

        per_100g = {
            "calories": _safe_float(row.get("calories")),
            "protein": _safe_float(row.get("protein")),
            "carbs": _safe_float(row.get("carbs")),
            "fat": _safe_float(row.get("fat")),
            "fiber": _safe_float(row.get("fiber")),
            "sugar": _safe_float(row.get("sugar")),
            "sodium": _safe_float(row.get("sodium")),
        }

        factor = grams / 100.0
        base = {
            "calories": _round_n(_mul(per_100g["calories"], factor)),
            "protein": _round_n(_mul(per_100g["protein"], factor), 1),
            "carbs": _round_n(_mul(per_100g["carbs"], factor), 1),
            "fat": _round_n(_mul(per_100g["fat"], factor), 1),
        }

        return {
            "food_name": food_name,
            "display_name": display,
            "category": _safe_str(row.get("category")),
            "serving_size": serving_label,
            "serving_grams": grams,
            "quantity_unit": qty_unit,
            "default_quantity": 1.0,
            "calories": base["calories"],
            "protein": base["protein"],
            "carbs": base["carbs"],
            "fat": base["fat"],
            "per_100g": per_100g,
            "source": "dataset",
        }

    def search(self, query: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
        if not query.strip() or not self._loaded:
            return []

        q = query.strip().lower()
        results: list[dict[str, Any]] = []
        seen: set[str] = set()

        def add(entry: dict[str, Any], score: float, source: str) -> None:
            key = entry["food_name"].lower()
            if key in seen:
                return
            seen.add(key)
            results.append(self._to_search_result(entry, score, source))

        # Exact match
        exact = self._by_name.get(q)
        if exact:
            add(exact, 100.0, "dataset")

        # Substring matches
        for entry in self._entries:
            name = entry["food_name"].lower()
            if q in name and name not in seen:
                add(entry, 90.0 if name.startswith(q) else 75.0, "dataset")

        # Fuzzy match via rapidfuzz
        if len(results) < limit:
            fuzzy = process.extract(
                q,
                self._names,
                scorer=fuzz.WRatio,
                limit=limit * 3,
            )
            for name, score, _ in fuzzy:
                if score < FUZZY_THRESHOLD:
                    continue
                entry = self._by_name.get(name.lower())
                if entry:
                    add(entry, float(score), "dataset")

        results.sort(key=lambda x: x["confidence_score"], reverse=True)
        return results[:limit]

    def get_by_name(self, food_name: str) -> dict[str, Any] | None:
        if not food_name.strip():
            return None
        key = food_name.strip().lower()
        if key in self._by_name:
            return self._to_detail(self._by_name[key], 100.0, "dataset")

        matches = self.search(food_name, limit=1)
        if matches and matches[0]["confidence_score"] >= HIGH_CONFIDENCE:
            entry = self._by_name.get(matches[0]["food_name"].lower())
            if entry:
                return self._to_detail(entry, matches[0]["confidence_score"], matches[0]["source"])
        return None

    def predict_food(self, food_name: str, nutrition: dict[str, float] | None = None) -> dict[str, Any]:
        """ML fallback when food is not in dataset."""
        if not self._ml_ready:
            raise RuntimeError("ML models not loaded. Run: python -m app.ml.pipeline")

        from app.ml.inference import predict_full

        if nutrition and all(nutrition.get(k) is not None for k in ("protein", "carbs", "fat")):
            ml_input = {k: float(nutrition.get(k) or 0) for k in (
                "protein", "carbs", "fat", "fiber", "sugar", "sodium", "calcium", "iron", "vitamin_c"
            )}
        else:
            # Use fuzzy best match macros as seed, or zeros
            seed = self.search(food_name, limit=1)
            if seed:
                entry = self._by_name.get(seed[0]["food_name"].lower())
                if entry:
                    ml_input = {
                        "protein": entry["per_100g"]["protein"] or 0,
                        "carbs": entry["per_100g"]["carbs"] or 0,
                        "fat": entry["per_100g"]["fat"] or 0,
                        "fiber": 0, "sugar": 0, "sodium": 0, "calcium": 0, "iron": 0, "vitamin_c": 0,
                    }
                else:
                    ml_input = {"protein": 5, "carbs": 15, "fat": 5, "fiber": 0, "sugar": 0,
                                "sodium": 0, "calcium": 0, "iron": 0, "vitamin_c": 0}
            else:
                ml_input = {"protein": 5, "carbs": 15, "fat": 5, "fiber": 0, "sugar": 0,
                            "sodium": 0, "calcium": 0, "iron": 0, "vitamin_c": 0}

        ml_result = predict_full(ml_input)
        grams, serving_label, qty_unit = infer_serving(food_name)
        factor = grams / 100.0
        per_100g_cal = ml_result["predicted_calories"]
        p_ratio = ml_input["protein"] / max(ml_input["protein"] + ml_input["carbs"] + ml_input["fat"], 1)
        c_ratio = ml_input["carbs"] / max(ml_input["protein"] + ml_input["carbs"] + ml_input["fat"], 1)
        f_ratio = ml_input["fat"] / max(ml_input["protein"] + ml_input["carbs"] + ml_input["fat"], 1)

        entry = {
            "food_name": food_name.strip(),
            "display_name": food_name.strip().title(),
            "category": ml_result["predicted_category"],
            "serving_size": serving_label,
            "serving_grams": grams,
            "quantity_unit": qty_unit,
            "default_quantity": 1.0,
            "calories": _round_n(per_100g_cal * factor),
            "protein": _round_n(ml_input["protein"] * factor, 1),
            "carbs": _round_n(ml_input["carbs"] * factor, 1),
            "fat": _round_n(ml_input["fat"] * factor, 1),
            "per_100g": {
                "calories": per_100g_cal,
                "protein": ml_input["protein"],
                "carbs": ml_input["carbs"],
                "fat": ml_input["fat"],
            },
            "source": "ml",
            "ml_prediction": ml_result,
        }
        return self._to_detail(entry, 70.0, "ml")

    def scale_nutrition(
        self,
        base_calories: float,
        base_protein: float,
        base_carbs: float,
        base_fat: float,
        quantity: float,
    ) -> dict[str, float]:
        q = max(quantity, 0.0)
        return {
            "calories": _round_n(base_calories * q),
            "protein": _round_n(base_protein * q, 1),
            "carbs": _round_n(base_carbs * q, 1),
            "fat": _round_n(base_fat * q, 1),
        }

    def log_food(
        self,
        food_name: str,
        quantity: float = 1.0,
        meal_type: str = "lunch",
    ) -> dict[str, Any]:
        detail = self.get_by_name(food_name)
        source = "dataset"
        confidence = detail["confidence_score"] if detail else 0.0

        if not detail or confidence < HIGH_CONFIDENCE:
            detail = self.predict_food(food_name)
            source = "ml"

        scaled = self.scale_nutrition(
            detail["calories"],
            detail["protein"],
            detail["carbs"],
            detail["fat"],
            quantity,
        )
        return {
            "food_name": detail["food_name"],
            "display_name": detail.get("display_name", detail["food_name"]),
            "meal_type": meal_type,
            "quantity": quantity,
            "serving_size": detail["serving_size"],
            "quantity_unit": detail.get("quantity_unit", DEFAULT_QUANTITY_UNIT),
            "category": detail["category"],
            "source": source,
            "confidence_score": detail.get("confidence_score", confidence),
            **scaled,
        }

    def _to_search_result(self, entry: dict[str, Any], score: float, source: str) -> dict[str, Any]:
        return {
            "food_name": entry["food_name"],
            "display_name": entry["display_name"],
            "category": entry["category"],
            "serving_size": entry["serving_size"],
            "quantity_unit": entry.get("quantity_unit", DEFAULT_QUANTITY_UNIT),
            "default_quantity": entry.get("default_quantity", 1.0),
            "calories": entry["calories"],
            "protein": entry["protein"],
            "carbs": entry["carbs"],
            "fat": entry["fat"],
            "confidence_score": round(min(score, 100.0) / 100.0, 2),
            "source": source,
        }

    def _to_detail(self, entry: dict[str, Any], score: float, source: str) -> dict[str, Any]:
        out = self._to_search_result(entry, score, source)
        out["display_name"] = entry.get("display_name", entry["food_name"].title())
        if entry.get("ml_prediction"):
            out["ml_prediction"] = entry["ml_prediction"]
        return out


def infer_serving(food_name: str) -> tuple[float, str, str]:
    name = food_name.lower()
    for pattern, grams, label, unit in SERVING_RULES:
        if re.search(pattern, name, re.IGNORECASE):
            return grams, label, unit
    return DEFAULT_SERVING_GRAMS, DEFAULT_SERVING_LABEL, DEFAULT_QUANTITY_UNIT


def _safe_float(val: Any) -> float | None:
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def _safe_str(val: Any) -> str | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    return s or None


def _mul(val: float | None, factor: float) -> float | None:
    if val is None:
        return None
    return val * factor


def _round_n(val: float | None, decimals: int = 0) -> float:
    if val is None:
        return 0.0
    return round(val, decimals)


# Singleton used by routes
food_service = FoodService()
