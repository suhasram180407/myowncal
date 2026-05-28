from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.session import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    breakfast_enabled = Column(Boolean, nullable=False, default=True)
    lunch_enabled = Column(Boolean, nullable=False, default=True)
    dinner_enabled = Column(Boolean, nullable=False, default=True)
    summary_enabled = Column(Boolean, nullable=False, default=True)

    breakfast_time = Column(String(8), nullable=False, default="08:00")
    lunch_time = Column(String(8), nullable=False, default="13:00")
    dinner_time = Column(String(8), nullable=False, default="20:00")
    summary_time = Column(String(8), nullable=False, default="21:00")

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notification_preferences")
