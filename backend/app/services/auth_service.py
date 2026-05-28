from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.services.calorie_engine import run_calorie_engine
from app.services.notification_service import get_or_create_notification_prefs


async def register_user(db: AsyncSession, name: str, email: str, password: str) -> User:
    # Check duplicate email
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=name,
        username=name.strip().lower().replace(" ", "_")[:100],
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await get_or_create_notification_prefs(db, user.id)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


async def update_profile(db: AsyncSession, user_id: int, data: dict) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Apply all provided fields
    for field, value in data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)

    # Recalculate calories if profile is complete
    if all([user.weight, user.height, user.age, user.gender, user.activity_level, user.goal]):
        result_cal = run_calorie_engine(
            user.weight, user.height, user.age,
            user.gender, user.activity_level, user.goal
        )
        user.maintenance_calories = result_cal["maintenance_calories"]
        user.target_calories = result_cal["target_calories"]

    return user


async def get_profile(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
