from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models import reminder
from app.models.reminder import ReminderRequest, ReminderResponse, Reminder
from app.Database.client import appointments_col, reminders_col


router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/", response_model=List[Reminder])
async def list_reminders():
    docs = await reminders_col.find().to_list(100)
    return docs

@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: str):
    doc = await reminders_col.find_one({"_id":reminder_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return doc

@router.post("/", response_model=Reminder)
async def create_reminder(reminder: Reminder):
    appt = await appointments_col.find_one({"_id":reminder.appointment_id})
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    await reminders_col.insert_one(reminder.dict())
    return reminder

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: str, reminder: Reminder):
    result = await reminders_col.replace_one({"_id":reminder_id}, reminder.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    result = await reminders_col.delete_one({"_id":reminder_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"status": "deleted"}





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