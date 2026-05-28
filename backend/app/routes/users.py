from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.user import ProfileUpdateRequest, ProfileResponse
from app.services.auth_service import get_profile, update_profile
from app.utils.jwt import get_current_user_id

router = APIRouter(prefix="/api/users", tags=["User Profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated user's profile including calculated calories."""
    return await get_profile(db, user_id)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    body: ProfileUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Update profile fields. Calorie targets are automatically recalculated
    when weight, height, age, gender, activity_level, and goal are all set.
    """
    return await update_profile(db, user_id, body.model_dump(exclude_none=True))
