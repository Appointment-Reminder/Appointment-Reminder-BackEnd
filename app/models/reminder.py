from pydantic import BaseModel

class ReminderRequest(BaseModel):
    appointment_id: str
    template: str


class ReminderResponse(BaseModel):
    message: str
    status: str
