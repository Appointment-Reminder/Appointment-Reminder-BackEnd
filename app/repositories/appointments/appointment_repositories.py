from datetime import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlalchemy.orm.sync import update
from sqlmodel import Session, select

from app.db.models.appointment import Appointment


class AppointmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def find_by_business(self, business_id: int, status: Optional[str] = None) -> Optional[Appointment]:
        query = select(Appointment).where(Appointment.business_id == business_id)

        if status:
            query = query.where(Appointment.status == status)
        query = query.options(selectinload(Appointment.user))
        return self.db.exec(query).all()

    def get_appointments_by_photographer(self, user_id: int, business_id: Optional[int] = None, status: Optional[str] = None):
        query = select(Appointment).where(Appointment.user_id == user_id)

        if business_id:
            query = query.where(Appointment.business_id == business_id)
        if status:
            query = query.where(Appointment.status == status)

        query = query.options(selectinload(Appointment.user))
        return self.db.exec(query).all()

    def get_appointment_by_id(self, appointment_id: int,user_id:Optional[int] = None, status : Optional[str] = None) -> Optional[Appointment]:
        query = select(Appointment).where(Appointment.id == appointment_id)
        if user_id:
            query = query.where(Appointment.user_id == user_id)
        if status:
            query = query.where(Appointment.status == status)

        query = query.options(selectinload(Appointment.user))

        return self.db.exec(query).first()

    def delete(self, appointment_id: int) -> bool:
        appointment = self.db.get(Appointment, appointment_id)

        if not appointment:
            return False

        self.db.delete(appointment)
        self.db.commit()
        return True

    def update(self, appointment_data: Appointment, appointment_id: int) -> Appointment:
        appointment = self.db.get(Appointment, appointment_id)

        if not appointment:
            return None

        update_data = appointment_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(appointment, key, value)

        appointment.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(appointment)
        return appointment