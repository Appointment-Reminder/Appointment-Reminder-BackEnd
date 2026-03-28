from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    """ Request schema for creating appointment"""
    client_name: str
    client_email: EmailStr
    client_phone: Optional[str] = None
    appointment_date: datetime

class AppointmentRead(BaseModel):
    """ Request schema for reading appointment"""
    id: int
    client_name: str
    client_email: str
    client_phone: Optional[str]
    appointment_date: datetime
    photographer_id: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
