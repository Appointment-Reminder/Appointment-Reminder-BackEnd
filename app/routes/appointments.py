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

