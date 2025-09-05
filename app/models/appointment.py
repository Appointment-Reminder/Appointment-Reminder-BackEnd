from pydantic import BaseModel
from typing import Optional

class Appointment(BaseModel):
    id: Optional[str]
    name: str
    surname: str
    phone: str
    email: Optional[str] = None
    time: str
    location: str
    photographer_id : Optional[int] = None
    balance_due: Optional[float] = 0.0
    notes: Optional[str] = None
    reminder_sent: Optional[bool] = False