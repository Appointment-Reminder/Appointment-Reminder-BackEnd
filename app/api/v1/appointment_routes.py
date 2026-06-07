from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from sqlalchemy.sql.annotation import Annotated

from app.models.appointment_model import AppointmentRead, AppointmentUpdate, AppointmentCreate
from app.repositories import business_member_repository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.services import appointment_service
from app.dependencies import APPOINTMENT_REPOSITORY_DEPENDENCY, CURRENT_USER_DEPENDENCY, BUSINESS_MEMBER_REPO_DEP

appointment_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

@appointment_router.post("/appointments", response_model=AppointmentRead, status_code=200)
def create_appointment(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        current_user: CURRENT_USER_DEPENDENCY,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        appointment_data: AppointmentCreate,
):
    return appointment_service.create_appointment_by_business_member(
        appointment_repository=appointment_repository,
        business_member_repo=business_member_repo,
        current_user=current_user,
        appointment_data=appointment_data,
    )

@appointment_router.get("/me", response_model=List[AppointmentRead], status_code=200)
def get_my_appointments(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        current_user: CURRENT_USER_DEPENDENCY,
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc"),
):
    """Get all appointments for the currently logged in photographer"""
    photographer_id = current_user.id
    appointments = appointment_service.get_assigned_appointments(current_user= current_user, appointment_repository=appointment_repository, status = status)
    return appointments

@appointment_router.get("/appointments/business/{business_id}", response_model=List[AppointmentRead], status_code=200)
def get_appointment_for_business(
        appointment_repository : APPOINTMENT_REPOSITORY_DEPENDENCY,
        business_member_repo :  BUSINESS_MEMBER_REPO_DEP,
        current_user : CURRENT_USER_DEPENDENCY,
        business_id: int,
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc")):
    """Get all appointments for the currently logged in user for business"""
    return appointment_service.get_appointments_by_business(
        current_user=current_user,
        appointment_repository=appointment_repository,
        business_member_repository=business_member_repo,
        business_id=business_id,
        status=status,
    )

@appointment_router.get("/appointments/business/{business_id}/appointments/{appointment_id}", response_model=AppointmentRead, status_code=200)
def get_single_appointment(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        business_id: int,
        appointment_id: int,
):
    """Get a single appointment for the currently logged in user for business"""
    return appointment_service.get_single_appointment(
        current_user=current_user,
        appointment_repository=appointment_repository,
        business_member_repository=business_member_repo,
        business_id=business_id,
        appointment_id=appointment_id,
    )

@appointment_router.patch("/appointments/business/{business_id}/appointments/{appointment_id}", response_model=AppointmentRead, status_code=200)
def update_single_appointment(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        business_id: int,
        appointment_id: int,
        appointment_data: AppointmentUpdate,
) -> AppointmentRead:
    """Update a single appointment for the currently logged in user"""
    return appointment_service.update_single_appointment(
        current_user=current_user,
        appointment_repository=appointment_repository,
        business_member_repository=business_member_repo,
        business_id=business_id,
        appointment_id=appointment_id,
        appointment_data=appointment_data,
    )

@appointment_router.delete("/appointments/{appointment_id}", status_code=200)
def delete_single_appointment(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        appointment_id: int,
):
    """delete an appointment for the admin or owner only of a business"""
    appointment_service.delete_single_appointment(
        current_user=current_user,
        appointment_repository=appointment_repository,
        business_member_repository=business_member_repo,
        appointment_id=appointment_id,
    )

@appointment_router.get("/businesses/{business_id}/appointments/{appointment_id}", response_model=AppointmentRead, status_code=200)
def get_single_appointment(
        appointment_repository: APPOINTMENT_REPOSITORY_DEPENDENCY,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        business_id: int,
        appointment_id: int,
):
    """Get a single appointment for the currently logged in user for business"""
    pass

@appointment_router.patch("/businesses/{business_id}/appointments/{appointment_id}/payments", response_model=AppointmentRead, status_code=200)
def update_appointment_payments(business_id: int, appointment_id: int):
    """Update the payments for the currently logged in user for business"""
    pass

@appointment_router.get("/businesses/{business_id}/appointments?needs_review=true", response_model=List[AppointmentRead], status_code=200)
def get_pending_review_appointments(business_id: int,needs_review: bool):
    """get all the appointments pending a review"""
    pass

