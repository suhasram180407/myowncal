from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from app.database.session import get_db
from app.schemas.meal import MealLogRequest, MealResponse
from app.services.meal_service import log_meal, get_meals_for_day, get_meals_history, delete_meal
from app.utils.jwt import get_current_user_id

router = APIRouter(prefix="/api/meals", tags=["Meal Logging"])


@router.post("/", response_model=MealResponse, status_code=201)
async def add_meal(
    body: MealLogRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Log a food entry. Automatically saved to the ML dataset pipeline."""
    return await log_meal(db, user_id, body.model_dump())


@router.get("/", response_model=list[MealResponse])
async def list_meals(
    day: Optional[date] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all meals for a given day (defaults to today)."""
    target_day = day or date.today()
    return await get_meals_for_day(db, user_id, target_day)


@router.get("/history", response_model=list[MealResponse])
async def meal_history(
    days: int = 30,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List meals for the last N days (newest first)."""
    return await get_meals_history(db, user_id, days=min(max(days, 1), 90))


@router.delete("/{meal_id}", status_code=204)
async def remove_meal(
    meal_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a meal entry."""
    await delete_meal(db, user_id, meal_id)
