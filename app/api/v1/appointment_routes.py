from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from sqlalchemy.sql.annotation import Annotated

from app.models.appointment_model import AppointmentRead
from app.services import appointment_service
from app.dependencies import APPOINTMENT_REPOSITORY_DEPENDENCY, CURRENT_USER_DEPENDENCY

appointment_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

@appointment_router.get("/me", response_model=List[AppointmentRead], status_code=200)
def get_my_appointments(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        current_user: CURRENT_USER_DEPENDENCY,
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc"),
):
    """Get all appointments for the currently logged in photographer"""
    photographer_id = current_user.id
    appointments = appointment_service.get_appointments_by_photographer(repo= appointment_repository, photographer_id=photographer_id, status = status)
    return appointments

@appointment_router.get("/me/{appointment_id}", response_model=AppointmentRead, status_code=200)
def get_my_appointment(
        appointment_id: int,
        appointment_repository : APPOINTMENT_REPOSITORY_DEPENDENCY,
        current_user : CURRENT_USER_DEPENDENCY
):

    photographer_id = current_user.id
    appointment = appointment_service.get_appointment_by_id(
        repo = appointment_repository,
        appointment_id = appointment_id,
        photographer_id = photographer_id,
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment