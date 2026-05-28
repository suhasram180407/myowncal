from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base


class MealTypeEnum(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snacks = "snacks"


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    food_name = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False, default="g")  # g, ml, piece, cup, plate

    # Nutrition per logged quantity
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=True, default=0.0)   # grams
    carbs = Column(Float, nullable=True, default=0.0)     # grams
    fats = Column(Float, nullable=True, default=0.0)      # grams

    meal_type = Column(Enum(MealTypeEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to user
    user = relationship("User", back_populates="meals")
