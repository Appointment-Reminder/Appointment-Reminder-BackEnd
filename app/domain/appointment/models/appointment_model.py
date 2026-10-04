from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from app.domain.addon.models.appointment_addon import AppointmentAddon
from app.domain.addon.models.unresolved_addon import UnresolvedAddon

from app.domain.appointment.models.appointment_state_machine import AppointmentStatus, AppointmentEvent, appointment_sm, \
    AppointmentCtx
from app.domain.user.models.user import User


@dataclass()
class Appointment:
    id: Optional[int]
    business_id: int
    member_id: Optional[int]
    form_id: Optional[int]

    # PACKAGE INFORMATION
    package_id: Optional[int]
    package_price_id: Optional[int]

    #CLIENT INFORMATION
    client_first_name: str
    client_last_name: str
    client_phone: Optional[str]
    client_email: Optional[str]
    referral_source: Optional[str]

    #PRICE
    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]

    #APPOINTMENT
    appointment_date: datetime
    appointment_location: Optional[str]
    appointment_duration: Optional[int]
    appointment_note: Optional[str]
    number_of_persons: Optional[int]
    privacy_opt_out: Optional[str]

    status: AppointmentStatus

    created_at: datetime
    updated_at: datetime

    addons: List[AppointmentAddon] = field(default_factory=list)
    unresolved_addons: List[UnresolvedAddon] = field(default_factory=list)

    def handle(self, event: AppointmentEvent) -> AppointmentCtx:
        ctx = AppointmentCtx(appointment_id=self.id)
        self.status = appointment_sm.handle(ctx, AppointmentStatus(self.status), event)
        return ctx