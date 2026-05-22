from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional
from app.db.models.business import Business
class Appointment(SQLModel, table=True):
    __tablename__ = 'appointments'

    id: Optional[int] = Field(default=None, primary_key=True)

    # client information
    client_name: str
    client_email: str
    client_phone: Optional[str] = None

    #appointment details
    appointment_date: datetime

    #link to business and photographer
    business_id: int = Field(foreign_key='businesses.id')
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    #status
    status: str = Field(default='pending')

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


