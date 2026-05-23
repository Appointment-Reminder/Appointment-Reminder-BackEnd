
from datetime import datetime
from typing import List, Optional

from app.db.models.appointment import Appointment
from app.models.appointment_model import AppointmentCreate, AppointmentUpdate
from app.repositories.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from models.user import User


def create_appointment(repository: AppointmentRepository, appointment_data: AppointmentCreate) -> Appointment:
    if appointment_data.business_id is None:
        return None

    appointment = Appointment(
        **appointment_data.dict()
    )
    return repository.create(appointment)

def get_appointments_by_business(current_user: User,
                                 appointment_repository: AppointmentRepository,
                                 business_member_repository: BusinessMemberRepository,
                                 business_id: int,
                                 status: Optional[str] = None) -> List[Appointment]:
    """Check the role of the current user in busines {business id}"""
    """Get list of appointment for business {business id} depending on role"""
    """if role is photographer only get the current user assigned appointment"""
    """if role is admin get all the appointment for the business"""
    """if status is set get the appointment for the business and status higher than the status"""
    return None

def get_single_appointment(
        current_user: User,
        appointment_repository: AppointmentRepository,
        business_member_repository: BusinessMemberRepository,
        business_id: int,
        appointment_id: int) -> Appointment:
    """Check the role of the current user in business {business id}"""
    """check that the appointment is either assigned to the user or user is owner or admin of the business"""
    """return the appointment"""
    return None;

def update_single_appointment(
        current_user: User,
        appointment_repository: AppointmentRepository,
        business_member_repository: BusinessMemberRepository,
        business_id: int,
        appointment_id: int,
        appointment_data: AppointmentUpdate
) -> Appointment:
    """ update a single appointment"""
    """check if the current user can update that appointment (is assigned or admin/owner)"""
    """update the appointment data"""
    """update the appointment updated date"""
    """return the updated appointment"""
    return None;

def delete_single_appointment(
        current_user: User,
        appointment_repository: AppointmentRepository,
        business_member_repository: BusinessMemberRepository,
        appointment_id: int
):
    """delete a single appointment"""
    """check if the current user is owner or admin"""
    """delete the appointment"""