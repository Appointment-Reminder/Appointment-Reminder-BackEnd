from fastapi import APIRouter, HTTPException
from app.models.appointment import Appointment
from typing import List

router = APIRouter(prefix="/appointments", tags=["appointments"])

#Dummy in memory storage
appointments_db = {
    "1": Appointment(id="1", name="Alice", surname="Smith", phone="+123456789",
                     email="alice@example.com", time="2025-09-10 15:00", location="Central Park"),
    "2": Appointment(id="2", name="Bob", surname="Johnson", phone="+987654321",
                     email="bob@example.com", time="2025-09-11 10:00", location="Studio A")
}

@router.get("/", response_model=List[Appointment])
def list_appointments():
    return list(appointments_db.values())

@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: str):
    appointment = appointments_db.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

