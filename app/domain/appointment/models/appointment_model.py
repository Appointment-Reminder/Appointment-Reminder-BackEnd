import datetime
from dataclasses import dataclass
from typing import Optional

from app.domain.user.models.user import User


@dataclass(frozen=True)
class Appointment:
    id: Optional[int]
    business_id: int
    user_id: Optional[int]
    form_id: int

    # PACKAGE INFORMATION
    package_id: Optional[int]
    package_price_id: Optional[int]

    #CLIENT INFORMATION
    client_first_name: str
    client_last_name: str
    client_phone: Optional[str]
    client_email: Optional[str]

    #PRICE
    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]

    #APPOINTMENT
    appointment_date: datetime
    appointment_location: Optional[str]
    appointment_duration: Optional[str]
    appointment_note: Optional[str]
    number_of_persons: Optional[int]
    privacy_opt_out: Optional[str]
    adds_ons: Optional[str]

    status: str
    created_at: datetime
    updated_at: datetime