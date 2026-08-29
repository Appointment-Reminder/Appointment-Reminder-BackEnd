from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query
from typing import Optional, List

from app.api.models.appointment_model import AppointmentRead, AppointmentCreate, AppointmentUpdate
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.appointment.service.appointment_service import AppointmentService
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.user.models.user import User

appointment_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    route_class=DishkaRoute
)

@appointment_router.post("/", response_model=AppointmentRead, status_code=200)
def create_appointment(
        appointment_service: FromDishka[AppointmentService],
        current_user: FromDishka[User],
        appointment_data: AppointmentCreate,
):
    return appointment_service.create_appointment_by_business_member(
        current_user=current_user,
        appointment=appointment_data,
    )

@appointment_router.get("/me", response_model=List[AppointmentRead], status_code=200)
def get_my_appointments(
        appointment_service: FromDishka[AppointmentService],
        current_user: FromDishka[User],
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc"),
):
    """Get all appointments for the currently logged in photographer"""
    appointments = appointment_service.get_assigned_appointments(current_user= current_user)
    return appointments

@appointment_router.get("/business/{business_id}", response_model=List[AppointmentRead], status_code=200)
def get_appointment_for_business(
        appointment_service: FromDishka[AppointmentService],
        current_user : FromDishka[User],
        business_id: int,
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc")):
    """Get all appointments for the currently loggedin user for business"""
    return appointment_service.get_appointments_by_business(
        current_user=current_user,
        business_id=business_id,
    )

@appointment_router.get("/business/{business_id}/appointments/{appointment_id}", response_model=AppointmentRead, status_code=200)
def get_single_appointment(
        appointment_service: FromDishka[AppointmentService],
        current_user: FromDishka[User],
        business_id: int,
        appointment_id: int,
):
    """Get a single appointment for the currently logged in user for business"""
    return appointment_service.get_single_appointment(
        current_user=current_user,
        business_id=business_id,
        appointment_id=appointment_id,
    )

@appointment_router.patch("/business/{business_id}/appointments/{appointment_id}", response_model=AppointmentRead, status_code=200)
def update_single_appointment(
        appointment_service: FromDishka[AppointmentService],
        current_user: FromDishka[User],
        business_id: int,
        appointment_id: int,
        appointment_data: AppointmentUpdate,
) -> AppointmentRead:
    """Update a single appointment for the currently logged in user"""
    return appointment_service.update_single_appointment(
        current_user=current_user,
        business_id=business_id,
        appointment_data=appointment_data,
    )

@appointment_router.delete("/{appointment_id}", status_code=200)
def delete_single_appointment(
        appointment_service: FromDishka[AppointmentService],
        current_user: FromDishka[User],
        appointment_id: int,
):
    """delete an appointment for the admin or owner only of a business"""
    appointment_service.delete_single_appointment(
        current_user=current_user,
        appointment_id=appointment_id,
    )

@appointment_router.get("{appointment_id}/businesses/{business_id}/", response_model=AppointmentRead, status_code=200)
def get_single_appointment(
        appointment_repository: FromDishka[AppointmentRepositoryPort],
        business_member_repo: FromDishka[BusinessMemberRepositoryPort],
        current_user: FromDishka[User],
        business_id: int,
        appointment_id: int,
):
    """Get a single appointment for the currently logged in user for business"""
    pass

@appointment_router.patch("{appointment_id}/businesses/{business_id}/payments", response_model=AppointmentRead, status_code=200)
def update_appointment_payments(business_id: int, appointment_id: int):
    """Update the payments for the currently logged in user for business"""
    pass

@appointment_router.get("/businesses/{business_id}/appointments?needs_review=true", response_model=List[AppointmentRead], status_code=200)
def get_pending_review_appointments(business_id: int,needs_review: bool):
    """get all the appointments pending a review"""
    pass

