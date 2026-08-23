from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


from app.domain.appointment.models.appointment_model import Appointment as AppointmentEntity
from app.adapters.sql_model_adapter.user.models.user import _to_domain as user_to_domain

class Appointment(SQLModel, table=True):
    __tablename__ = 'appointments'

    id: Optional[int] = Field(default=None, primary_key=True)
    #keys
    business_id: int = Field(foreign_key='businesses.id')
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    package_id: int = Field(foreign_key='package.id')
    package_price_id: int = Field(foreign_key='package_price.id')
    form_id: int = Field(foreign_key='business_member_form.id')

    # client information
    client_name: str
    client_email: str
    client_phone: Optional[str] = None

    #price info
    price_at_booking: float
    deposit_amount: float
    remaining_amount: float
    commission_percent_at_booking: float
    commision_amount_at_booking: float
    is_personal: bool


    #appointment details
    appointment_date: datetime

    #status
    status: str = Field(default='pending')

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship()

def _to_domain(row: Appointment) -> AppointmentEntity:
    return AppointmentEntity(
        id=row.id,
        business_id=row.business_id,
        user_id=row.user_id,
        package_id=row.package_id,
        package_price_id=row.package_price_id,
        form_id=row.form_id,
        client_name=row.client_name,
        client_email=row.client_email,
        client_phone=row.client_phone,
        price_at_booking=row.price_at_booking,
        deposit_amount=row.deposit_amount,
        remaining_amount=row.remaining_amount,
        commission_percent_at_booking=row.commission_percent_at_booking,
        commission_amount_at_booking=row.commision_amount_at_booking,  # note: typo in row field name
        is_personal=row.is_personal,
        appointment_date=row.appointment_date,
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
        user= user_to_domain(row.user) if row.user else None,
    )


def _apply_to_row(row: Appointment, entity: AppointmentEntity) -> None:
    # entity is frozen — only the row gets mutated, never the dataclass
    row.client_name = entity.client_name
    row.client_email = entity.client_email
    row.client_phone = entity.client_phone
    row.appointment_date = entity.appointment_date
    row.user_id = entity.user_id
    row.status = entity.status