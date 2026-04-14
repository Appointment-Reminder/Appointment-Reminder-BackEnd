from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional

from app.db.models.appointment import Appointment
from app.models.appointment_model import AppointmentCreate


def create_appointment(db: Session, appointment_data: AppointmentCreate, photographer_id: Optional[int]) -> Appointment:
    appointment = Appointment(
        **appointment_data.dict(),
        user_id=photographer_id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments(db: Session, photographer_id: Optional[int] = None, status: Optional[str] = None) -> Appointment:
    """Get appointments with optional filters"""
    query = select(Appointment)

    if photographer_id:
        query = query.where(Appointment.photographer_id == photographer_id)
    if status:
        query = query.where(Appointment.status == status)

    return db.execute(query).all()

def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.get(Appointment, appointment_id)

def update_appointment(db: Session, appointment_id: int, appointment_data: Appointment) -> Optional[Appointment]:
    """Update an appointment"""
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        return None

    update_data = appointment_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appointment, key, value)

    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db: Session, appointment_id: int) -> bool:
    """Delete an appointment"""
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        return False

    db.delete(appointment)
    db.commit()
    return True