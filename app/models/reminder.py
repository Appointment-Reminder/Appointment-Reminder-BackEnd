from pydantic import BaseModel
from typing import Optional

class ReminderRequest(BaseModel):
    appointment_id: str
    template: str


class ReminderResponse(BaseModel):
    message: str
    status: str

class Reminder(BaseModel):
    id: Optional[str]
    appointment_id: str
    template: str
    status: str = "pending"