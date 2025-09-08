from fastapi import APIRouter, HTTPException, Depends
from app.models.reminder import ReminderRequest, ReminderResponse
from app.Database.client import appointments_col


router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/preview", response_model=ReminderResponse)
async def preview_reminder(req: ReminderRequest):
    appointment = await appointments_col.find_one({"_id": req.appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    message = req.template.format(
        Client=f"{appointment['name']} {appointment['surname']}",
        Time = appointment['time'],
        Location=appointment['location']
    )

    return ReminderResponse(status="preview", message=message)

@router.post("/send", response_model=ReminderResponse)
async def send_reminder(req: ReminderRequest):
    appointment = await appointments_col.find_one({"_id": req.appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    message = req.template.format(
        Client=f"{appointment['name']} {appointment['surname']}",
        Time = appointment['time'],
        Location=appointment['location']
    )

    # TODO: integrate real sending (WhatsApp/SMS/email)
    print(f"Sending message to {appointment['name']} {appointment['surname']}: {message}")

    return ReminderResponse(status="sent", message=message)