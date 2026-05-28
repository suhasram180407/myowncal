from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class GoalEnum(str, enum.Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class ActivityEnum(str, enum.Enum):
    sedentary = "sedentary"    # desk job, no exercise
    light = "light"            # 1-3 days/week
    moderate = "moderate"      # 3-5 days/week
    active = "active"          # 6-7 days/week
    athlete = "athlete"        # twice/day training


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Physical profile
    age = Column(Integer, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    weight = Column(Float, nullable=True)   # kg
    height = Column(Float, nullable=True)   # cm

    # Goals
    goal = Column(Enum(GoalEnum), nullable=True)
    activity_level = Column(Enum(ActivityEnum), nullable=True)

    # Calculated by the calorie engine
    maintenance_calories = Column(Float, nullable=True)
    target_calories = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    daily_summaries = relationship("DailySummary", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = relationship(
        "NotificationPreference", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    ai_insights = relationship("AIInsight", back_populates="user", cascade="all, delete-orphan")
