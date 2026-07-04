from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from app.db.models.business import Business
from app.db.models.package.package import Package
from app.db.models.package.package_price import PackagePrice
from app.db.models.Member.business_member_form import BusinessMemberForm


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


