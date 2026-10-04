import datetime
from typing import List, Optional

from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.addon.service.appointment_addon_hydration import attach_addons
from app.domain.addon.service.appointment_addon_service import AppointmentAddonService
from app.domain.appointment.errors.appointment_error import AppointmentError
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentEvent, AppointmentStatus
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import MemberRole
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.user.models.user import User


class AppointmentService:
    def __init__(self,
                 appointment_repo: AppointmentRepositoryPort,
                 business_member_repo: BusinessMemberRepositoryPort,
                 business_guard: BusinessGuard,
                 appointment_addon_repo: AppointmentAddonRepositoryPort,
                 appointment_addon_service: AppointmentAddonService,
                 ):
        self.appointment_repo = appointment_repo
        self.business_member_repo = business_member_repo
        self.business_guard = business_guard
        self.appointment_addon_repo = appointment_addon_repo
        self.appointment_addon_service = appointment_addon_service

    def _with_addons(self, appointments: List[Appointment]) -> List[Appointment]:
        return attach_addons(appointments, self.appointment_addon_repo)

    def create_appointment(self, appointment: Appointment) -> Appointment:
        if appointment.business_id is None:
            raise AppointmentError()

        appointment = Appointment(
            **appointment.dict()
        )
        return self.appointment_repo.create(appointment)

    def create_appointment_by_business_member(self, appointment : Appointment ,current_user: User) -> Appointment:
        self.business_guard.ensure_admin_or_owner(appointment.business_id, current_user.id)
        if appointment.member_id is not None:
            m = self.business_member_repo.get_member_by_id(appointment.member_id)
            if not m or m.business_id != appointment.business_id:
                raise AppointmentError()

        now = datetime.now()
        entity = Appointment(
            id=None, form_id=None, referral_source=None,
            appointment_location=None, appointment_duration=None, appointment_note=None,
            number_of_persons=None, privacy_opt_out=None,
            status=AppointmentStatus.NEW, created_at=now, updated_at=now,
            **appointment.model_dump(),
        )
        entity.handle(AppointmentEvent.CREATE)
        if entity.member_id is not None:
            entity.handle(AppointmentEvent.ASSIGN)
        return self.appointment_repo.create(entity)

    def get_assigned_appointments(self, current_user: User) -> List[Appointment]:
        result = []
        for member in self.business_member_repo.get_my_business_members(current_user.id):
            result.extend(self.appointment_repo.get_appointment_by_photographer(member_id=member.id) or [])
        return self._with_addons(result)

    def get_appointments_by_business(self, business_id: int, current_user: User,
                                     has_unresolved_addons: Optional[bool] = None) -> List[Appointment]:
        member = self.business_guard.ensure_is_a_member(business_id, current_user.id)
        if member.role in (MemberRole.OWNER, MemberRole.ADMIN):
            appointments = self.appointment_repo.find_by_business(business_id)
        else:
            appointments = self.appointment_repo.get_appointment_by_photographer(member.id, business_id) or []

        if has_unresolved_addons is not None:
            flagged = self.appointment_addon_repo.appointment_ids_with_unresolved_addons(business_id)
            appointments = [a for a in appointments if (a.id in flagged) == has_unresolved_addons]
        return self._with_addons(appointments)

    def get_single_appointment(self, business_id: int, appointment_id: int, current_user: User) -> Appointment:
        if not self.business_guard.ensure_is_a_member(business_id, current_user.id):
            raise AppointmentError()

        appointment = self.appointment_repo.get_appointment_by_id(appointment_id)

        if not appointment or appointment.business_id != business_id:
            raise AppointmentError()

        member = self.business_member_repo.get_member(business_id, current_user.id)

        is_admin = member.role in [MemberRole.OWNER, MemberRole.ADMIN]
        is_assigned = appointment.member_id == member.id

        if not (is_assigned or is_admin):
            raise AppointmentError()

        return self._with_addons([appointment])[0]

    def update_single_appointment(self, business_id: int, appointment_id:int, appointment: Appointment,  current_user: User) -> Appointment:
        member = self.business_guard.ensure_is_a_member(business_id=business_id, user_id=current_user.id)
        found = self.appointment_repo.get_appointment_by_id(appointment_id)
        if not found or found.business_id != business_id:
            raise AppointmentError()

        is_admin = member.role in (MemberRole.OWNER, MemberRole.ADMIN)
        if not (is_admin or found.member_id == member.id):
            raise AppointmentError()

        if appointment.member_id is not None:
            if not is_admin:
                raise AppointmentError()
            target = self.business_member_repo.get_member_by_id(appointment.member_id)
            if not target or target.business_id != business_id:
                raise AppointmentError()
            if found.status == AppointmentStatus.NEEDS_ASSIGNMENT:
                found.handle(AppointmentEvent.ASSIGN)
                self.appointment_repo.update_status(found)
            self.appointment_addon_service.assign_member(found, target.id)

        updated = self.appointment_repo.update(appointment=appointment, appointment_id=appointment_id)
        return self._with_addons([updated])[0]

    def delete_single_appointment(self, appointment_id: int, current_user: User) :
        appointment = self.appointment_repo.get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentError

        if not self.business_guard.ensure_is_a_member(business_id=appointment.business_id, user_id=current_user.id):
            raise AppointmentError()

        if not self.business_guard.ensure_admin_or_owner(business_id=appointment.business_id, user_id=current_user.id):
            raise AppointmentError()

        self.appointment_repo.delete(appointment_id)

    def advance(self, business_id: int, appointment_id: int, event: AppointmentEvent, current_user: User) -> Appointment:
        self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)

        appointment = self.get_single_appointment(business_id, appointment_id, current_user)
        appointment.handle(event)
        if event == AppointmentEvent.UNASSIGN:
            self.appointment_addon_service.unassign_member(appointment)
        return self._with_addons([self.appointment_repo.update_status(appointment)])[0]