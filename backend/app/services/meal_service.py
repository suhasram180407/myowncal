from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from datetime import date, timedelta
from app.models.meal import Meal, MealTypeEnum
from app.services.daily_summary_service import upsert_daily_summary


def _normalize_meal_type(meal_type) -> MealTypeEnum:
    if isinstance(meal_type, MealTypeEnum):
        return meal_type
    value = str(meal_type)
    if value == "snack":
        return MealTypeEnum.snacks
    return MealTypeEnum(value)


async def log_meal(db: AsyncSession, user_id: int, data: dict) -> Meal:
    payload = {**data}
    payload["meal_type"] = _normalize_meal_type(payload["meal_type"])
    meal = Meal(user_id=user_id, **payload)
    db.add(meal)
    await db.flush()
    meal_day = meal.created_at.date() if meal.created_at else date.today()
    await upsert_daily_summary(db, user_id, meal_day)
    return meal


async def get_meals_for_day(db: AsyncSession, user_id: int, day: date) -> list[Meal]:
    result = await db.execute(
        select(Meal).where(
            Meal.user_id == user_id,
            func.date(Meal.created_at) == day,
        )
    )
    return list(result.scalars().all())


async def get_meals_history(
    db: AsyncSession, user_id: int, days: int = 30
) -> list[Meal]:
    since = date.today() - timedelta(days=days)
    result = await db.execute(
        select(Meal)
        .where(Meal.user_id == user_id, func.date(Meal.created_at) >= since)
        .order_by(Meal.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_meal(db: AsyncSession, user_id: int, meal_id: int) -> None:
    result = await db.execute(select(Meal).where(Meal.id == meal_id, Meal.user_id == user_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_day = meal.created_at.date() if meal.created_at else date.today()
    await db.delete(meal)
    await db.flush()
    await upsert_daily_summary(db, user_id, meal_day)
