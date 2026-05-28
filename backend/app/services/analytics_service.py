from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from app.models.meal import Meal
from app.models.user import User


async def get_daily_summary(db: AsyncSession, user_id: int, day: date) -> dict:
    """
    Aggregates all meals for a user on a given day.
    Returns consumed macros and remaining calories vs target.
    """
    # Get user target calories
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    target = user.target_calories or 2000.0  # fallback if profile incomplete

    # Aggregate macros from meals on this day using SQL
    result = await db.execute(
        select(
            func.coalesce(func.sum(Meal.calories), 0).label("calories"),
            func.coalesce(func.sum(Meal.protein), 0).label("protein"),
            func.coalesce(func.sum(Meal.carbs), 0).label("carbs"),
            func.coalesce(func.sum(Meal.fats), 0).label("fats"),
            func.count(Meal.id).label("meal_count"),
        ).where(
            Meal.user_id == user_id,
            func.date(Meal.created_at) == day,
        )
    )
    row = result.one()

    consumed = float(row.calories)
    return {
        "date": str(day),
        "target_calories": target,
        "calories_consumed": consumed,
        "calories_remaining": round(target - consumed, 2),
        "protein_g": float(row.protein),
        "carbs_g": float(row.carbs),
        "fats_g": float(row.fats),
        "meal_count": row.meal_count,
    }
