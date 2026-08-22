import datetime
from dataclasses import dataclass
from typing import Optional

from app.domain.user.models.user import User


@dataclass(frozen=True)
class Appointment:
    id: Optional[int]

    business_id: int
    user_id: int
    package_id: int
    package_price_id: int
    form_id: int

    client_name: str
    client_email: str
    client_phone: Optional[str]

    price_at_booking: float
    deposit_amount: float
    remaining_amount: float
    commission_percent_at_booking: float
    commission_amount_at_booking: float
    is_personal: bool

    appointment_date: datetime

    status: str
    created_at: datetime
    updated_at: datetime
    user: User