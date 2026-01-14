from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class Appointment(SQLModel, table=True):
    __tablename__ = 'appointments'

    id: Optional[int] = Field(default=None, primary_key=True)

