from fastapi import APIRouter, HTTPException, Depends
from app.models.reminder import ReminderRequest, ReminderResponse
from app.routes.appointments import appointments_db


router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/preview", response_model=ReminderResponse)
def preview_reminder(req: ReminderRequest):
    appointment = appointments_db.get(req.appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    message = req.template.format(
        Client=f"{appointment.name} {appointment.surname}",
        Time = appointment.time,
        Location=appointment.location
    )

    return ReminderResponse(status="preview", message=message)

@router.post("/send", response_model=ReminderResponse)
def send_reminder(req: ReminderRequest):
    appointment = appointments_db.get(req.appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    message = req.template.format(
        Client=f"{appointment.name} {appointment.surname}",
        Time = appointment.time,
        Location=appointment.location
    )

    # TODO: integrate real sending (WhatsApp/SMS/email)
    print(f"Sending message to {appointment.name} {appointment.surname}: {message}")

    return ReminderResponse(status="sent", message=message)