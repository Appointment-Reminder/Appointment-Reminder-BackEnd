from datetime import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from app.domain.appointment.models.appointment_model import Appointment as AppointmentEntity
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort

from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment as AppointmentSQL
from app.adapters.sql_model_adapter.appointment.models.appointment import _to_domain, _apply_to_row


class SQLModelAppointmentRepositoryAdapter(AppointmentRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(AppointmentSQL).options(selectinload(AppointmentSQL.user))

    def create(self, appointment: AppointmentEntity) -> AppointmentEntity:
        sql_appointment = AppointmentSQL(
            business_id=appointment.business_id,
            user_id=appointment.user_id,
            package_id=appointment.package_id,
            package_price_id=appointment.package_price_id,
            form_id=appointment.form_id,
            client_name=appointment.client_name,
            client_email=appointment.client_email,
            client_phone=appointment.client_phone,
            price_at_booking=appointment.price_at_booking,
            deposit_amount=appointment.deposit_amount,
            remaining_amount=appointment.remaining_amount,
            commission_percent_at_booking = appointment.commission_percent_at_booking,
            commision_amount_at_booking = appointment.commission_amount_at_booking,
            appointment_date = appointment.appointment_date,
            status = appointment.status,
            created_at = appointment.created_at,
            updated_at = appointment.updated_at,
        )

        self.db.add(sql_appointment)
        self.db.commit()
        self.db.refresh(sql_appointment, attribute_names=["user"])
        return _to_domain(sql_appointment)

    def find_by_business(self, business_id: int, status: Optional[str] = None) -> Optional[AppointmentEntity]:
        query = self._base_query().where(AppointmentSQL.business_id == business_id)

        if status:
            query = query.where(AppointmentSQL.status == status)
        result = self.db.exec(query).all()
        return [ _to_domain(row) for row in result ] if result else None

    def get_appointment_by_photographer(self, user_id: int, business_id: Optional[int] = None,
                                        status: Optional[str] = None) -> Optional[AppointmentEntity]:
        query = self._base_query().where(AppointmentSQL.user_id == user_id)

        if business_id:
            query = query.where(AppointmentSQL.business_id == business_id)
        if status:
            query = query.where(AppointmentSQL.status == status)

        query = query.options(selectinload(AppointmentSQL.user))
        result = self.db.exec(query).all()
        return [_to_domain(item) for item in result] if result else None

    def get_appointment_by_id(self, appointment_id: int, user_id: Optional[int] = None, status: Optional[str] = None) -> \
    Optional[AppointmentEntity]:
        row = self.db.exec(
            self._base_query().where(AppointmentSQL.id == appointment_id)
        ).first()
        return _to_domain(row) if row else None

    def update(self, appointment: AppointmentEntity, appointment_id: int) -> AppointmentEntity:
        row = self.db.get(AppointmentSQL, appointment_id)
        if not row:
            return None
        _apply_to_row(row, appointment)
        row.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(row, attribute_names=["user"])
        return _to_domain(row)

    def delete(self, appointment_id: int) -> bool:
        appointment = self.db.get(AppointmentSQL, appointment_id)

        if not appointment:
            return False

        self.db.delete(appointment)
        self.db.commit()
        return True