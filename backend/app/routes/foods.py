"""Food search, details, ML predict, and log endpoints (dataset + ML pipeline)."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.food_service import food_service

router = APIRouter(prefix="/foods", tags=["Foods"])


class FoodSearchItem(BaseModel):
    food_name: str
    display_name: str | None = None
    category: str | None = None
    serving_size: str
    quantity_unit: str | None = "serving"
    default_quantity: float = 1.0
    calories: float
    protein: float
    carbs: float
    fat: float
    confidence_score: float
    source: str


class PredictRequest(BaseModel):
    food_name: str = Field(..., min_length=1)
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    fiber: float | None = 0.0
    sugar: float | None = 0.0
    sodium: float | None = 0.0


class LogFoodRequest(BaseModel):
    food_name: str = Field(..., min_length=1)
    quantity: float = Field(1.0, gt=0)
    meal_type: str = "lunch"


@router.get("/search", response_model=list[FoodSearchItem])
async def search_foods(q: str = Query(..., min_length=1)):
    """Fuzzy search over the food dataset."""
    if not food_service.loaded:
        raise HTTPException(status_code=503, detail="Food dataset not loaded")
    results = food_service.search(q)
    if not results:
        try:
            predicted = food_service.predict_food(q)
            return [FoodSearchItem.model_validate(predicted)]
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
    return [FoodSearchItem.model_validate(r) for r in results]


@router.get("/details/{food_name:path}", response_model=FoodSearchItem)
async def food_details(food_name: str):
    """Exact or high-confidence fuzzy lookup."""
    if not food_service.loaded:
        raise HTTPException(status_code=503, detail="Food dataset not loaded")
    detail = food_service.get_by_name(food_name)
    if detail:
        return FoodSearchItem.model_validate(detail)
    try:
        predicted = food_service.predict_food(food_name)
        return FoodSearchItem.model_validate(predicted)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict", response_model=FoodSearchItem)
async def predict_food(body: PredictRequest):
    """ML prediction when food is not in dataset."""
    nutrition = None
    if body.protein is not None and body.carbs is not None and body.fat is not None:
        nutrition = body.model_dump(exclude={"food_name"})
    try:
        result = food_service.predict_food(body.food_name, nutrition)
        return FoodSearchItem.model_validate(result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/log")
async def log_food(body: LogFoodRequest):
    """Return quantity-scaled nutrition for a food log entry."""
    if not food_service.loaded:
        raise HTTPException(status_code=503, detail="Food dataset not loaded")
    try:
        return food_service.log_food(body.food_name, body.quantity, body.meal_type)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
