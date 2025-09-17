from fastapi import APIRouter, HTTPException
from app.models.appointment import Appointment
from app.Database.client import appointments_col
from typing import List

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/", response_model=List[Appointment])
async def list_appointments():
    docs = await appointments_col.find().to_list(100)
    return docs

@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    doc = await appointments_col.find_one({"_id": appointment_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return doc

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: Appointment):
    await appointments_col.insert_one(appointment.dict())
    return appointment

@router.put("/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment: Appointment):
    result =await appointments_col.replace_one({"_id": appointment_id}, appointment.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    result = await appointments_col.delete_one({"_id": appointment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"status": "deleted"}