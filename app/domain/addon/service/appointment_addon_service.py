from datetime import datetime
from typing import Callable, Optional

from app.domain.addon.errors.addon_errors import AddonError, AppointmentAddonsLocked, NoAddonPriceInEffect
from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import commission_in_effect
from app.domain.addon.models.addon_price import price_in_effect
from app.domain.addon.models.appointment_addon import (
    AppointmentAddon, snapshot_appointment_addon, with_quantity,
)
from app.domain.addon.models.appointment_totals import fold_in_addon, fold_out_addon
from app.domain.addon.port.addon_commission_repository_port import AddonCommissionRepositoryPort
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import MemberRole
from app.domain.user.models.user import User

# Add-ons are plain edits, open until the appointment is closed out.
EDITABLE_STATUSES = frozenset({
    AppointmentStatus.NEW,
    AppointmentStatus.NEEDS_ASSIGNMENT,
    AppointmentStatus.PENDING,
    AppointmentStatus.PENDING_SELECTION,
    AppointmentStatus.PENDING_EDITING,
    AppointmentStatus.PENDING_REVIEW,
})


class AppointmentAddonService:
    """Staff edits of the Add-ons booked on an appointment. Every edit keeps the appointment totals in step."""

    def __init__(
        self,
        appointment_repo: AppointmentRepositoryPort,
        appointment_addon_repo: AppointmentAddonRepositoryPort,
        addon_repo: AddonRepositoryPort,
        price_repo: AddonPriceRepositoryPort,
        commission_repo: AddonCommissionRepositoryPort,
        business_guard: BusinessGuard,
        addon_guard: AddonGuard,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self.appointment_repo = appointment_repo
        self.appointment_addon_repo = appointment_addon_repo
        self.addon_repo = addon_repo
        self.price_repo = price_repo
        self.commission_repo = commission_repo
        self.business_guard = business_guard
        self.addon_guard = addon_guard
        self.clock = clock

    def add_addon(self, business_id: int, appointment_id: int, addon_id: int, quantity: int,
                  current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        addon = self._ensure_bookable(addon_id, business_id)
        self._ensure_quantity_allowed(addon, quantity)
        if self.appointment_addon_repo.get(appointment_id, addon_id) is not None:
            raise AddonError()

        line = self._snapshot(appointment, addon, quantity)
        line.appointment_id = appointment_id
        line = self.appointment_addon_repo.add(line)
        fold_in_addon(appointment, line)
        return self._save(appointment)

    def remove_addon(self, business_id: int, appointment_id: int, addon_id: int, current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        line = self._ensure_line(appointment_id, addon_id)

        self.appointment_addon_repo.remove(line.id)
        fold_out_addon(appointment, line)
        return self._save(appointment)

    def set_quantity(self, business_id: int, appointment_id: int, addon_id: int, quantity: int,
                     current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        line = self._ensure_line(appointment_id, addon_id)
        self._ensure_quantity_allowed(self.addon_guard.ensure_addon_exist(addon_id), quantity)

        updated = with_quantity(line, quantity)
        self.appointment_addon_repo.update(updated)
        fold_out_addon(appointment, line)
        fold_in_addon(appointment, updated)
        return self._save(appointment)

    # helpers
    def _load_editable(self, business_id: int, appointment_id: int, current_user: User) -> Appointment:
        member = self.business_guard.ensure_is_a_member(business_id, current_user.id)
        appointment = self.appointment_repo.get_appointment_by_id(appointment_id)
        if appointment is None or appointment.business_id != business_id:
            raise AddonError()

        is_admin = member.role in (MemberRole.OWNER, MemberRole.ADMIN)
        if not (is_admin or appointment.member_id == member.id):
            raise AddonError()

        if AppointmentStatus(appointment.status) not in EDITABLE_STATUSES:
            raise AppointmentAddonsLocked()
        return appointment

    def _ensure_bookable(self, addon_id: int, business_id: int) -> Addon:
        addon = self.addon_guard.ensure_addon_exist(addon_id)
        if addon.business_id != business_id or not addon.is_active:
            raise AddonError()
        return addon

    @staticmethod
    def _ensure_quantity_allowed(addon: Addon, quantity: int) -> None:
        if quantity < 1 or (not addon.has_quantity and quantity != 1):
            raise AddonError()

    def _ensure_line(self, appointment_id: int, addon_id: int) -> AppointmentAddon:
        line = self.appointment_addon_repo.get(appointment_id, addon_id)
        if line is None:
            raise AddonError()
        return line

    def _snapshot(self, appointment: Appointment, addon: Addon, quantity: int,
                  raw_label: Optional[str] = None) -> AppointmentAddon:
        """Freeze the price and the assigned member's commission as they are now."""
        now = self.clock()
        price = price_in_effect(self.price_repo.get_history(addon.id), now)
        if price is None:
            raise NoAddonPriceInEffect()

        commission = None
        if appointment.member_id is not None:
            commission = commission_in_effect(
                self.commission_repo.get_history(appointment.member_id, addon.id), appointment.member_id, addon.id, now)
        return snapshot_appointment_addon(addon, price, commission, quantity=quantity, raw_label=raw_label)

    def _save(self, appointment: Appointment) -> Appointment:
        self.appointment_repo.update_totals(appointment)
        appointment.addons = self.appointment_addon_repo.list_for_appointment(appointment.id)
        appointment.unresolved_addons = self.appointment_addon_repo.list_unresolved_for_appointments(
            [appointment.id]).get(appointment.id, [])
        return appointment
