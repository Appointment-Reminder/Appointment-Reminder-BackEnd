from typing import List, Optional

from fastapi import HTTPException

from app.db.models.appointment import Appointment
from app.models.appointment_model import AppointmentCreate, AppointmentUpdate
from app.repositories.appointments.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.db.models.business_member import MemberRole
from app.db.models.user import User


def create_appointment(repository: AppointmentRepository, appointment_data: AppointmentCreate) -> Appointment:
    if appointment_data.business_id is None:
        return None

    appointment = Appointment(
        **appointment_data.dict()
    )
    return repository.create(appointment)

def create_appointment_by_business_member(appointment_repository: AppointmentRepository,business_member_repo: BusinessMemberRepository, current_user: User, appointment_data: AppointmentCreate) -> Appointment:

    if not is_user_in_business(business_member_repo, business_id=appointment_data.business_id, user_id=current_user.id):
        raise HTTPException(status_code=403, detail="You cannot create appointment for this business")

    if not is_user_in_business(business_member_repo, user_id=appointment_data.user_id, business_id=appointment_data.business_id):
        raise HTTPException(status_code=403, detail="the assigned photographer is not a member of this business")

    if not is_user_admin_or_owner(business_member_repo, business_id=appointment_data.business_id, user_id=current_user.id) and appointment_data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create appointment for yourself in this business")

    return create_appointment(repository=appointment_repository, appointment_data=appointment_data)

def is_user_in_business(
        business_member_repository: BusinessMemberRepository,
        business_id: int,
        user_id: int) -> bool:
    member = business_member_repository.get_member(business_id, user_id)
    if not member or not member.is_active:
        return False
    return True

def is_user_admin_or_owner(
        business_member_repository: BusinessMemberRepository,
        business_id: int,
        user_id: int) -> bool:
    member = business_member_repository.get_member(business_id, user_id)
    return member.role in [MemberRole.OWNER, MemberRole.ADMIN]

def get_assigned_appointments(
        current_user: User,
        appointment_repository: AppointmentRepository,
        status: Optional[str] = None
):
    return appointment_repository.get_appointments_by_photographer(user_id=current_user.id, status=status)

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

    if not is_user_in_business(business_member_repository, business_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this business")

    if is_user_admin_or_owner(business_member_repository, business_id, current_user.id):
        appointments = appointment_repository.find_by_business(business_id, status)
    else:
        appointments = appointment_repository.get_appointments_by_photographer(current_user.id, business_id, status)

    return appointments

def get_single_appointment(
        current_user: User,
        appointment_repository: AppointmentRepository,
        business_member_repository: BusinessMemberRepository,
        business_id: int,
        appointment_id: int) -> Appointment:
    """Check the role of the current user in business {business id}"""
    """check that the appointment is either assigned to the user or user is owner or admin of the business"""
    """return the appointment"""

    if not is_user_in_business(business_member_repository, business_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this business")

    appointment = appointment_repository.get_appointment_by_id(appointment_id)

    if not appointment or appointment.business_id != business_id:
        raise HTTPException(status_code=404, detail="Appointment not found")

    is_admin = is_user_admin_or_owner(business_member_repository, business_id, current_user.id)
    is_assigned = appointment.user_id == current_user.id

    if not (is_assigned or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment")

    return appointment;

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

    print(f"receive appointment update {appointment_data}")

    if not is_user_in_business(business_member_repository, business_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this business")

    appointment = appointment_repository.get_appointment_by_id(appointment_id)
    if not appointment or appointment.business_id != business_id:
        raise HTTPException(status_code=404, detail="Appointment not found")

    is_admin = is_user_admin_or_owner(business_member_repository, business_id, current_user.id)
    is_assigned = appointment.user_id == current_user.id

    if not (is_assigned or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment")

    if not business_member_repository.get_member(business_id, appointment_data.user_id):
        raise HTTPException(status_code=404, detail="New user assigned is not a member of this business")

    return appointment_repository.update(appointment_data = appointment_data, appointment_id=appointment_id);

def delete_single_appointment(
        current_user: User,
        appointment_repository: AppointmentRepository,
        business_member_repository: BusinessMemberRepository,
        appointment_id: int
):
    """delete a single appointment"""
    """check if the current user is owner or admin"""
    """delete the appointment"""

    appointment = appointment_repository.get_appointment_by_id(appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if not is_user_in_business(business_member_repository, appointment.business_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this business")

    if not is_user_admin_or_owner(business_member_repository, appointment.business_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this appointment")

    appointment_repository.delete(appointment_id)
