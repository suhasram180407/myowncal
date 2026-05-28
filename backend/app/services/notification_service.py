from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification_preference import NotificationPreference


DEFAULT_PREFS = {
    "breakfast_enabled": True,
    "lunch_enabled": True,
    "dinner_enabled": True,
    "summary_enabled": True,
    "breakfast_time": "08:00",
    "lunch_time": "13:00",
    "dinner_time": "20:00",
    "summary_time": "21:00",
}


async def get_or_create_notification_prefs(
    db: AsyncSession, user_id: int
) -> NotificationPreference:
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    prefs = result.scalar_one_or_none()
    if prefs:
        return prefs
    prefs = NotificationPreference(user_id=user_id, **DEFAULT_PREFS)
    db.add(prefs)
    await db.flush()
    return prefs


async def update_notification_prefs(
    db: AsyncSession, user_id: int, data: dict
) -> NotificationPreference:
    prefs = await get_or_create_notification_prefs(db, user_id)
    for key, value in data.items():
        if hasattr(prefs, key) and value is not None:
            setattr(prefs, key, value)
    await db.flush()
    return prefs
