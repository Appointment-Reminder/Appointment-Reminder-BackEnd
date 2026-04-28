
from datetime import datetime
from typing import List, Optional

from app.db.models.appointment import Appointment
from app.models.appointment_model import AppointmentCreate
from app.repositories.appointment_repositories import AppointmentRepository


def create_appointment(repository: AppointmentRepository, appointment_data: AppointmentCreate, photographer_id: Optional[int]) -> Appointment:
    appointment = Appointment(
        **appointment_data.dict(),
        user_id=photographer_id
    )
    return repository.create(appointment)

def get_appointments_by_photographer(repository: AppointmentRepository, photographer_id: int, status: Optional[str] = None) -> List[Appointment]:
    """Get all appointments for a specific photographer"""
    return repository.get_appointments_by_photographer(photographer_id, status)

def get_appointment_by_id(repository: AppointmentRepository, appointment_id: int, photographer_id: Optional[int] = None ) -> Optional[Appointment]:
    return repository.get_appointments_by_id(appointment_id, photographer_id)

def update_appointment(repository: AppointmentRepository, appointment_id: int, appointment_data: Appointment) -> Optional[Appointment]:
    """Update an appointment"""
    return repository.update(appointment_data, appointment_id)


def delete_appointment(repository: AppointmentRepository, appointment_id: int) -> bool:
    """Delete an appointment"""
    return repository.delete(repository, appointment_id)