from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class Appointment(SQLModel, table=True):
    __tablename__ = 'appointments'

    id: Optional[int] = Field(default=None, primary_key=True)

    client_name: str
    client_email: str
    client_phone: Optional[str] = None

    appointment_date: datetime


