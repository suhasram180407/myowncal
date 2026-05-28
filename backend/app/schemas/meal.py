from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.models.meal import MealTypeEnum


class MealLogRequest(BaseModel):
    food_name: str
    quantity: float
    unit: str = "g"
    calories: float
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fats: Optional[float] = 0.0
    meal_type: MealTypeEnum

    @field_validator("meal_type", mode="before")
    @classmethod
    def normalize_meal_type(cls, v):
        if v == "snack":
            return MealTypeEnum.snacks
        return v

    @field_validator("calories")
    @classmethod
    def calories_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Calories must be greater than 0")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class MealResponse(BaseModel):
    id: int
    food_name: str
    quantity: float
    unit: str
    calories: float
    protein: Optional[float]
    carbs: Optional[float]
    fats: Optional[float]
    meal_type: MealTypeEnum
    created_at: datetime

    class Config:
        from_attributes = True
