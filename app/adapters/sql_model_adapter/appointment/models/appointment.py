from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


from app.domain.appointment.models.appointment_model import Appointment as AppointmentEntity
from app.adapters.sql_model_adapter.user.models.user import _to_domain as user_to_domain
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus


class Appointment(SQLModel, table=True):
    __tablename__ = 'appointments'

    id: Optional[int] = Field(default=None, primary_key=True)
    #keys
    business_id: int = Field(foreign_key='businesses.id')
    member_id: Optional[int] = Field(default=None, foreign_key="business_members.id")
    form_id: Optional[int] = Field(foreign_key='jotform_forms.id')


    package_id: int = Field(foreign_key='package.id')
    package_price_id: int = Field(foreign_key='package_price.id')


    # client information
    client_first_name: Optional[str]
    client_last_name: Optional[str]
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    referral_source: Optional[str] = None

    #price info
    price_at_booking: float
    deposit_amount: float
    remaining_amount: float
    commission_percent_at_booking: Optional[float] = Field(default = 0)
    commision_amount_at_booking: Optional[float]= Field(default = 0)

    #appointment details
    appointment_date: datetime
    appointment_location: Optional[str]
    appointment_duration: Optional[int]
    appointment_note: Optional[str]
    number_of_persons: Optional[int] = Field(default = 0)
    privacy_opt_out: Optional[str]

    #status
    status: str = Field(default='pending')

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

def _to_domain(row: Appointment) -> AppointmentEntity:
    return AppointmentEntity(
        id=row.id,
        business_id=row.business_id,
        member_id=row.member_id,
        package_id=row.package_id,
        package_price_id=row.package_price_id,
        form_id=row.form_id,
        client_first_name=row.client_first_name,
        client_last_name=row.client_last_name,
        client_email=row.client_email,
        client_phone=row.client_phone,
        referral_source=row.referral_source,

        price_at_booking=row.price_at_booking,
        deposit_amount=row.deposit_amount,
        remaining_amount=row.remaining_amount,
        commission_percent_at_booking=row.commission_percent_at_booking,
        commission_amount_at_booking=row.commision_amount_at_booking,


        appointment_date=row.appointment_date,
        appointment_location=row.appointment_location,
        appointment_duration=row.appointment_duration,
        appointment_note=row.appointment_note,
        number_of_persons=row.number_of_persons,
        privacy_opt_out=row.privacy_opt_out,

        status=AppointmentStatus(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _apply_to_row(row: Appointment, entity: AppointmentEntity) -> None:
    # entity is frozen — only the row gets mutated, never the dataclass

    if entity.client_first_name is not None:
        row.client_first_name = entity.client_first_name
    if entity.client_last_name is not None:
        row.client_last_name = entity.client_last_name
    if entity.client_email is not None:
        row.client_email = entity.client_email
    if entity.client_phone is not None:
        row.client_phone = entity.client_phone

    if entity.appointment_date is not None:
        row.appointment_date = entity.appointment_date
    if entity.appointment_location is not None:
        row.appointment_location = entity.appointment_location
    if entity.appointment_duration is not None:
        row.appointment_duration = entity.appointment_duration
    if entity.appointment_note is not None:
        row.appointment_note = entity.appointment_note
    if entity.number_of_persons is not None:
        row.number_of_persons = entity.number_of_persons
    if entity.privacy_opt_out is not None:
        row.privacy_opt_out = entity.privacy_opt_out
    if entity.member_id is not None:
        row.member_id = entity.member_id
