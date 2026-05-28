from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/predict", tags=["Nutrition Prediction"])


class NutritionInput(BaseModel):
    """
    Nutrition values per 100g serving.
    Only protein, carbs, fat are required.
    Micronutrients improve accuracy but are optional.
    """
    protein:   float
    carbs:     float
    fat:       float
    fiber:     Optional[float] = 0.0
    sugar:     Optional[float] = 0.0
    sodium:    Optional[float] = 0.0
    calcium:   Optional[float] = 0.0
    iron:      Optional[float] = 0.0
    vitamin_c: Optional[float] = 0.0


class PredictionResponse(BaseModel):
    predicted_calories:      float
    predicted_category:      str
    category_probabilities:  dict[str, float]
    input_features:          dict[str, float]


@router.post("/", response_model=PredictionResponse)
def predict_nutrition(body: NutritionInput):
    """
    Predict calories and food category from nutrition values.

    - Uses GradientBoostingRegressor for calorie prediction (R2=0.98)
    - Uses RandomForestClassifier for category prediction (Acc=91.9%)
    - All values must be per 100g serving
    """
    try:
        from app.ml.inference import predict_full
        result = predict_full(body.model_dump())
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Models not trained yet. Run: python -m app.ml.pipeline. Error: {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calories-only")
def predict_calories_only(body: NutritionInput):
    """Predict only calories — faster, skips category classification."""
    try:
        from app.ml.inference import predict_calories
        calories = predict_calories(body.model_dump())
        return {"predicted_calories": calories}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
