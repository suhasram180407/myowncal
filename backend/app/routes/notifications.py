from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.notification import NotificationPrefsResponse, NotificationPrefsUpdate
from app.services.notification_service import get_or_create_notification_prefs, update_notification_prefs
from app.utils.jwt import get_current_user_id

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/preferences", response_model=NotificationPrefsResponse)
async def get_preferences(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await get_or_create_notification_prefs(db, user_id)


@router.put("/preferences", response_model=NotificationPrefsResponse)
async def put_preferences(
    body: NotificationPrefsUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await update_notification_prefs(db, user_id, body.model_dump(exclude_none=True))
