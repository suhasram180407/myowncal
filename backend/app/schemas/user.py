from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import GenderEnum, GoalEnum, ActivityEnum


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    weight: Optional[float] = None   # kg
    height: Optional[float] = None   # cm
    goal: Optional[GoalEnum] = None
    activity_level: Optional[ActivityEnum] = None


class ProfileResponse(BaseModel):
    id: int
    username: Optional[str] = None
    name: str
    email: EmailStr
    age: Optional[int]
    gender: Optional[GenderEnum]
    weight: Optional[float]
    height: Optional[float]
    goal: Optional[GoalEnum]
    activity_level: Optional[ActivityEnum]
    maintenance_calories: Optional[float]
    target_calories: Optional[float]

    class Config:
        from_attributes = True
