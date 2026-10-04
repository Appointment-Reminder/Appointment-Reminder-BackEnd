from datetime import datetime
from typing import Callable, List, Optional, Tuple

from app.domain.addon.errors.addon_errors import (
    AddonError, AppointmentAddonsLocked, AppointmentNotPriced, NoAddonPriceInEffect)
from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import commission_in_effect
from app.domain.addon.models.addon_price import price_in_effect
from app.domain.addon.models.appointment_addon import (
    AppointmentAddon, snapshot_appointment_addon, with_commission, with_quantity,
)
from app.domain.addon.service.appointment_addon_hydration import attach_addons
from app.domain.addon.service.appointment_totals import fold_in_addon, fold_out_addon, swap_addon_commission
from app.domain.addon.port.addon_commission_repository_port import AddonCommissionRepositoryPort
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import MemberRole
from app.domain.package.port.package_repository_port import PackageRepositoryPort
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
        package_repo: PackageRepositoryPort,
        price_repo: AddonPriceRepositoryPort,
        commission_repo: AddonCommissionRepositoryPort,
        business_guard: BusinessGuard,
        addon_guard: AddonGuard,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self.appointment_repo = appointment_repo
        self.appointment_addon_repo = appointment_addon_repo
        self.addon_repo = addon_repo
        self.package_repo = package_repo
        self.price_repo = price_repo
        self.commission_repo = commission_repo
        self.business_guard = business_guard
        self.addon_guard = addon_guard
        self.clock = clock

    def add_addon(self, business_id: int, appointment_id: int, addon_id: int, quantity: int,
                  current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        self._book(appointment, addon_id, quantity)
        return self._save(appointment)

    def remove_addon(self, business_id: int, appointment_id: int, addon_id: int, current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        line = self._ensure_appointment_addon(appointment_id, addon_id)

        self.appointment_addon_repo.remove(line.id)
        fold_out_addon(appointment, line)
        return self._save(appointment)

    def set_quantity(self, business_id: int, appointment_id: int, addon_id: int, quantity: int,
                     current_user: User) -> Appointment:
        appointment = self._load_editable(business_id, appointment_id, current_user)
        line = self._ensure_appointment_addon(appointment_id, addon_id)
        self._ensure_quantity_allowed(self.addon_guard.ensure_addon_exist(addon_id), quantity)

        updated = with_quantity(line, quantity)
        self.appointment_addon_repo.update(updated)
        fold_out_addon(appointment, line)
        fold_in_addon(appointment, updated)
        return self._save(appointment)

    def replace_addons(self, business_id: int, appointment_id: int, desired: List[Tuple[int, int]],
                       current_user: User) -> Appointment:
        """Make the appointment carry exactly the desired (addon_id, quantity) set, all or nothing.

        Lines already booked keep their frozen price and commission (only the quantity moves), new ones are frozen
        now, missing ones are removed. Everything is checked before anything is written, then written in one go.
        """
        appointment = self._load_editable(business_id, appointment_id, current_user)
        addon_ids = [addon_id for addon_id, _ in desired]
        if len(set(addon_ids)) != len(addon_ids):
            raise AddonError()

        current = {line.addon_id: line for line in self.appointment_addon_repo.list_for_appointment(appointment_id)}
        removed = [line for addon_id, line in current.items() if addon_id not in addon_ids]
        requantified: List[Tuple[AppointmentAddon, AppointmentAddon]] = []
        added: List[AppointmentAddon] = []
        for addon_id, quantity in desired:
            line = current.get(addon_id)
            if line is None:
                added.append(self._new_line(appointment, addon_id, quantity))
                continue
            self._ensure_quantity_allowed(self.addon_guard.ensure_addon_exist(addon_id), quantity)
            if quantity != line.quantity:
                requantified.append((line, with_quantity(line, quantity)))

        for line in removed:
            fold_out_addon(appointment, line)
        for old, new in requantified:
            fold_out_addon(appointment, old)
            fold_in_addon(appointment, new)
        for line in added:
            fold_in_addon(appointment, line)

        self.appointment_addon_repo.apply_changes(
            appointment, removed_ids=[line.id for line in removed],
            updated=[new for _, new in requantified], added=added)
        return attach_addons([appointment], self.appointment_addon_repo)[0]

    def resolve_unresolved_addon(self, business_id: int, appointment_id: int, unresolved_id: int, addon_id: int,
                           current_user: User, quantity: int = 1) -> Appointment:
        """Book the picked Add-on for an Unresolved Add-on, at today's price and the assigned member's commission."""
        appointment = self._load_editable(business_id, appointment_id, current_user)
        unresolved = self.appointment_addon_repo.get_unresolved_addon(unresolved_id)
        if unresolved is None or unresolved.appointment_id != appointment_id or unresolved.is_resolved:
            raise AddonError()

        self._book(appointment, addon_id, quantity, raw_label=unresolved.raw_label)

        unresolved.resolved_addon_id = addon_id
        unresolved.resolved_at = self.clock()
        self.appointment_addon_repo.update_unresolved_addon(unresolved)
        return self._save(appointment)

    def assign_member(self, appointment: Appointment, member_id: int) -> Appointment:
        """Make the member the commission recipient: each Appointment Add-on takes the member's commission now."""
        if appointment.member_id == member_id:
            return appointment
        now = self.clock()
        appointment.member_id = member_id
        for line in self.appointment_addon_repo.list_for_appointment(appointment.id):
            commission = commission_in_effect(
                self.commission_repo.get_history(member_id, line.addon_id), member_id, line.addon_id, now)
            self._recommission(appointment, line, commission)
        return self._save(appointment)

    def unassign_member(self, appointment: Appointment) -> Appointment:
        """Nobody earns the Add-ons any more: their commission goes back to unset."""
        appointment.member_id = None
        for line in self.appointment_addon_repo.list_for_appointment(appointment.id):
            self._recommission(appointment, line, None)
        if (appointment.commission_amount_at_booking or 0) <= 0:
            appointment.commission_amount_at_booking = None
        return self._save(appointment)

    # helpers
    def _book(self, appointment: Appointment, addon_id: int, quantity: int, raw_label: Optional[str] = None) -> None:
        """Freeze the add-on as an Appointment Add-on of the appointment and fold it into the totals."""
        line = self._new_line(appointment, addon_id, quantity, raw_label=raw_label)
        if self.appointment_addon_repo.get(appointment.id, addon_id) is not None:
            raise AddonError()
        fold_in_addon(appointment, self.appointment_addon_repo.add(line))

    def _new_line(self, appointment: Appointment, addon_id: int, quantity: int,
                  raw_label: Optional[str] = None) -> AppointmentAddon:
        """The checked, frozen line for an Add-on about to be booked; nothing is written."""
        if appointment.price_at_booking is None:
            raise AppointmentNotPriced()
        addon = self._ensure_bookable(addon_id, appointment.business_id, appointment)
        self._ensure_quantity_allowed(addon, quantity)

        line = self._snapshot(appointment, addon, quantity, raw_label=raw_label)
        line.appointment_id = appointment.id
        return line

    def _recommission(self, appointment: Appointment, line: AppointmentAddon, commission) -> None:
        updated = with_commission(line, commission)
        self.appointment_addon_repo.update(updated)
        swap_addon_commission(appointment, line, updated)

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

    def _ensure_bookable(self, addon_id: int, business_id: int, appointment: Appointment) -> Addon:
        addon = self.addon_guard.ensure_addon_exist(addon_id)
        if addon.business_id != business_id or not addon.is_active:
            raise AddonError()
        if addon.category_id is not None and addon.category_id != self._package_category_id(appointment):
            raise AddonError()
        return addon

    def _package_category_id(self, appointment: Appointment) -> Optional[int]:
        if appointment.package_id is None:
            return None
        package = self.package_repo.get_package_by_id(appointment.package_id)
        return package.category_id if package else None

    @staticmethod
    def _ensure_quantity_allowed(addon: Addon, quantity: int) -> None:
        if quantity < 1 or (not addon.has_quantity and quantity != 1):
            raise AddonError()

    def _ensure_appointment_addon(self, appointment_id: int, addon_id: int) -> AppointmentAddon:
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
        return attach_addons([appointment], self.appointment_addon_repo)[0]
