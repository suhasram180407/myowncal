from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from app.database.session import get_db
from app.services.daily_summary_service import get_stored_daily_summary, upsert_daily_summary
from app.utils.jwt import get_current_user_id

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/daily-summary")
async def daily_summary(
    day: Optional[date] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns calories consumed, remaining, and macro breakdown for a day.
    Defaults to today if no date is provided.
    """
    target_day = day or date.today()
    await upsert_daily_summary(db, user_id, target_day)
    return await get_stored_daily_summary(db, user_id, target_day)


@router.get("/daily")
async def daily_analytics(
    day: Optional[date] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Alias for daily-summary used by mobile clients."""
    target_day = day or date.today()
    await upsert_daily_summary(db, user_id, target_day)
    return await get_stored_daily_summary(db, user_id, target_day)
