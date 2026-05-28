"""Legacy /api/food routes — delegates to FoodService."""
from fastapi import APIRouter, Query

from app.services.food_service import food_service

router = APIRouter(prefix="/api/food", tags=["Food Search (Legacy)"])


@router.get("/search")
async def search_food(q: str = Query(..., min_length=1)):
    results = food_service.search(q.strip())
    return {"query": q, "results": results, "count": len(results)}


@router.get("/lookup")
async def lookup_food(name: str = Query(...)):
    food = food_service.get_by_name(name.strip())
    if not food:
        return {"found": False, "food": None}
    return {"found": True, "food": food}
