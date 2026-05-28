from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_summary import DailySummary
from app.models.user import User
from app.services.analytics_service import get_daily_summary


async def upsert_daily_summary(db: AsyncSession, user_id: int, day: date) -> DailySummary:
    """Recalculate totals from meals and persist daily_summaries row."""
    summary = await get_daily_summary(db, user_id, day)

    result = await db.execute(
        select(DailySummary).where(
            DailySummary.user_id == user_id,
            DailySummary.date == day,
        )
    )
    row = result.scalar_one_or_none()

    if row is None:
        row = DailySummary(
            user_id=user_id,
            date=day,
            total_calories=summary["calories_consumed"],
            total_protein=summary["protein_g"],
            total_carbs=summary["carbs_g"],
            total_fat=summary["fats_g"],
            remaining_calories=summary["calories_remaining"],
        )
        db.add(row)
    else:
        row.total_calories = summary["calories_consumed"]
        row.total_protein = summary["protein_g"]
        row.total_carbs = summary["carbs_g"]
        row.total_fat = summary["fats_g"]
        row.remaining_calories = summary["calories_remaining"]

    await db.flush()
    return row


async def get_stored_daily_summary(db: AsyncSession, user_id: int, day: date) -> dict:
    """Return stored summary or compute live from meals."""
    result = await db.execute(
        select(DailySummary).where(
            DailySummary.user_id == user_id,
            DailySummary.date == day,
        )
    )
    row = result.scalar_one_or_none()
    if row:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        target = user.target_calories if user and user.target_calories else 2000.0
        return {
            "date": str(day),
            "target_calories": target,
            "calories_consumed": row.total_calories,
            "calories_remaining": row.remaining_calories,
            "protein_g": row.total_protein,
            "carbs_g": row.total_carbs,
            "fats_g": row.total_fat,
            "meal_count": None,
            "stored": True,
        }
    live = await get_daily_summary(db, user_id, day)
    live["stored"] = False
    return live
