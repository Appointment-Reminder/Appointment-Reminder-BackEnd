from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

from app.models.userModel import UserRead


class AppointmentCreate(BaseModel):
    """ Request schema for creating appointment"""
    client_name: str
    client_email: EmailStr
    client_phone: Optional[str] = None
    user_id: Optional[int] = None
    business_id: Optional[int] = None
    appointment_date: datetime

    @field_validator("business_id")
    @classmethod
    def business_id_validator(cls, v) -> str:
        if not v:
            raise ValueError("business_id cannot be empty")
        if v < 0:
            raise ValueError("business_id cannot be negative")
        return v

class AppointmentRead(BaseModel):
    """ Request schema for reading appointment"""
    id: int
    client_name: str
    client_email: str
    client_phone: Optional[str]
    appointment_date: datetime
    user_id: Optional[int]
    business_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    user: Optional[UserRead] = None

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    client_name: str
    client_email: EmailStr
    client_phone: Optional[str]
    appointment_date: datetime
    user_id: Optional[int]

