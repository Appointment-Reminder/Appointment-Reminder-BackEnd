import datetime
from dataclasses import dataclass
from typing import Optional

from app.domain.user.models.user import User


@dataclass(frozen=True)
class Appointment:
    id: Optional[int]
    business_id: int
    user_id: Optional[int]
    package_id: Optional[int]  # was: int — a needs_assignment appointment has no package match
    package_price_id: Optional[int]
    form_id: int

    client_name: str
    client_email: str
    client_phone: Optional[str]

    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]
    is_personal: Optional[bool]

    appointment_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    user: Optional[User]