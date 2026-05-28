from pydantic import BaseModel
from typing import Optional


class NotificationPrefsResponse(BaseModel):
    breakfast_enabled: bool
    lunch_enabled: bool
    dinner_enabled: bool
    summary_enabled: bool
    breakfast_time: str
    lunch_time: str
    dinner_time: str
    summary_time: str

    class Config:
        from_attributes = True


class NotificationPrefsUpdate(BaseModel):
    breakfast_enabled: Optional[bool] = None
    lunch_enabled: Optional[bool] = None
    dinner_enabled: Optional[bool] = None
    summary_enabled: Optional[bool] = None
    breakfast_time: Optional[str] = None
    lunch_time: Optional[str] = None
    dinner_time: Optional[str] = None
    summary_time: Optional[str] = None
