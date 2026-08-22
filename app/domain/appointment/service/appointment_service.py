from typing import List

from app.domain.appointment.errors.appointment_error import AppointmentError
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.user.models.user import User
from app.services.business.BusinessGuard import BusinessGuard


class AppointmentService:
    def __init__(self,
                 appointment_repo: AppointmentRepositoryPort,
                 business_member_repo: BusinessMemberRepositoryPort,
                 business_guard: BusinessGuard,
                 ):
        self.appointment_repo = appointment_repo
        self.business_member_repo = business_member_repo
        self.business_guard = business_guard

    def create_appointment(self, appointment: Appointment) -> Appointment:
        if appointment.business_id is None:
            raise AppointmentError()

        appointment = Appointment(
            **appointment.dict()
        )
        return self.appointment_repo.create(appointment)

    def create_appointment_by_business_member(self, appointment : Appointment ,current_user: User) -> Appointment:
        if not self.business_guard.ensure_is_a_member(appointment.business_id, appointment.user_id):
            raise AppointmentError()

        if not self.business_guard.ensure_admin_or_owner(business_id=appointment.business_id, user_id=current_user.id):
            raise AppointmentError()

        return self.create_appointment( appointment=appointment )

    def get_assigned_appointments(self, current_user: User) -> List[Appointment]:
        return self.appointment_repo.get_appointments_by_photographer(user_id=current_user.id)

    def get_appointments_by_business(self,business_id: int, current_user: User) -> List[Appointment]:
        if not self.business_guard.ensure_is_a_member(business_id=business_id, user_id=current_user.id):
            raise AppointmentError()

        if self.business_guard.ensure_admin_or_owner(business_id, current_user.id):
            appointments = self.appointment_repo.find_by_business(business_id)
        else:
            appointments = self.appointment_repo.get_appointments_by_photographer(current_user.id, business_id)

        return appointments

    def get_single_appointment(self, business_id: int, appointment_id: int, current_user: User) -> Appointment:
        if not self.business_guard.ensure_is_a_member(business_id, current_user.id):
            raise AppointmentError()

        appointment = self.appointment_repo.get_appointment_by_id(appointment_id)

        if not appointment or appointment.business_id != business_id:
            raise AppointmentError()

        is_admin = self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        is_assigned = appointment.user_id == current_user.id

        if not (is_assigned or is_admin):
            raise AppointmentError()

        return appointment;

    def update_single_appointment(self, business_id: int, appointment: Appointment,  current_user: User) -> Appointment:
        if not self.business_guard.ensure_is_a_member(business_id, current_user.id):
            raise AppointmentError()

        appointment = self.appointment_repo.get_appointment_by_id(appointment.id)
        if not appointment or appointment.business_id != business_id:
            raise AppointmentError()

        is_admin = self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)
        is_assigned = appointment.user_id == current_user.id

        if not (is_assigned or is_admin):
            raise AppointmentError()

        if not self.business_member_repo.get_member(business_id, appointment.user_id):
            raise AppointmentError()

        return self.appointment_repo.update(appointment_data=appointment, appointment_id=appointment.id);

    def delete_single_appointment(self, appointment_id: int, current_user: User) :
        appointment = self.appointment_repo.get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentError

        if not self.business_guard.ensure_is_a_member(business_id=appointment.business_id, user_id=current_user.id):
            raise AppointmentError()

        if not self.business_guard.ensure_admin_or_owner(business_id=appointment.business_id, user_id=current_user.id):
            raise AppointmentError()

        self.appointment_repo.delete(appointment_id)