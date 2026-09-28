from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

from app.api.models.userModel import UserRead


class AppointmentCreate(BaseModel):
    """ Request schema for creating appointment"""
    member_id: Optional[int] = None
    business_id: Optional[int] = None

    package_id: Optional[int]
    package_price_id: Optional[int]

    client_first_name: str
    client_last_name: str
    client_phone: Optional[str]
    client_email: Optional[str]

    appointment_date: datetime
    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]


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
    business_id: int
    member_id: Optional[int]
    form_id: Optional[int]

    # PACKAGE INFORMATION
    package_id: Optional[int]
    package_price_id: Optional[int]

    # CLIENT INFORMATION
    client_first_name: str
    client_last_name: str
    client_phone: Optional[str]
    client_email: Optional[str]
    referral_source: Optional[datetime]

    # PRICE
    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]

    # APPOINTMENT
    appointment_date: datetime
    appointment_location: Optional[str]
    appointment_duration: Optional[int]
    appointment_note: Optional[str]
    number_of_persons: Optional[int]
    privacy_opt_out: Optional[str]
    adds_ons: Optional[str]

    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = None

    appointment_date: Optional[datetime] = None
    appointment_location: Optional[str] = None
    appointment_duration: Optional[str] = None
    appointment_note: Optional[str] = None
    number_of_persons: Optional[int] = None
    privacy_opt_out: Optional[str] = None
    adds_ons: Optional[str] = None

    member_id: Optional[int] = None

