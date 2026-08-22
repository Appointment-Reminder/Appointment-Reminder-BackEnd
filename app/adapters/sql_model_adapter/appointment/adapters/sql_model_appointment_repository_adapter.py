import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort


class SQLModelAppointmentRepositoryAdapter(AppointmentRepositoryPort):

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

    def get_appointment_by_photographer(self, user_id: int, business_id: Optional[int] = None,
                                        status: Optional[str] = None) -> Optional[Appointment]:
        query = select(Appointment).where(Appointment.user_id == user_id)

        if business_id:
            query = query.where(Appointment.business_id == business_id)
        if status:
            query = query.where(Appointment.status == status)

        query = query.options(selectinload(Appointment.user))
        return self.db.exec(query).all()

    def get_appointment_by_id(self, appointment_id: int, user_id: Optional[int] = None, status: Optional[str] = None) -> \
    Optional[Appointment]:
        query = select(Appointment).where(Appointment.id == appointment_id)
        if user_id:
            query = query.where(Appointment.user_id == user_id)
        if status:
            query = query.where(Appointment.status == status)

        query = query.options(selectinload(Appointment.user))

        return self.db.exec(query).first()

    def update(self, appointment: Appointment, appointment_id: int) -> Appointment:
        appointment = self.db.get(Appointment, appointment_id)

        if not appointment:
            return None

        update_data = appointment.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(appointment, key, value)

        appointment.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def delete(self, appointment_id: int) -> bool:
        appointment = self.db.get(Appointment, appointment_id)

        if not appointment:
            return False

        self.db.delete(appointment)
        self.db.commit()
        return True