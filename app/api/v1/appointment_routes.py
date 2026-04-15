from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List, Annotated
from sqlmodel import Session

from app.db.models.user import User
from app.db.session import get_session
from app.models.appointment_model import AppointmentRead
from app.services import appointment_service
from app.services.user_service import get_current_user

appointment_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

@appointment_router.get("/me", response_model=List[AppointmentRead], status_code=200)
def get_my_appointments(
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc"),
        session: Session = Depends(get_session),
        current_user= Depends(get_current_user)
):
    """Get all appointments for the currently logged in photographer"""
    #TODO: Get photographer_id from authenticated user
    photographer_id = current_user.id
    print(f"Logged in photographer id {photographer_id}")

    appointments = appointment_service.get_appointments_by_photographer(db =session, photographer_id=photographer_id, status = status)

    return appointments

@appointment_router.get("/me/{appointment_id}", response_model=AppointmentRead, status_code=200)
def get_my_appointment(
        appointment_id: int,
        session: Session = Depends(get_session),
        current_user = Depends(get_current_user)
):
    """
    Get a specific appointment for the currently loggedin photographer
    :param appointment_id:
    :param session:
    :param current_user:
    :return:
    """

    photographer_id = current_user.id
    appointment = appointment_service.get_appointment_by_id(
        db = session,
        appointment_id = appointment_id,
        photographer_id = photographer_id,
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment