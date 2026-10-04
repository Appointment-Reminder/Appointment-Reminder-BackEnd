from dishka.integrations.fastapi import DishkaRoute, FromDishka, DishkaSyncRoute
from fastapi import APIRouter, Query, Depends
from typing import Optional, List

from app.api.models.addon.appointment_addon_model import (
    AppointmentAddonCreate, AppointmentAddonQuantityUpdate, UnresolvedAddonResolve)
from app.api.models.appointment_model import AppointmentRead, AppointmentCreate, AppointmentUpdate
from app.domain.addon.service.appointment_addon_service import AppointmentAddonService
from app.domain.appointment.models.appointment_state_machine import AppointmentEvent
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.appointment.service.appointment_service import AppointmentService
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.user.models.user import User
from app.domain.user.service.user_service import oauth2_bearer

appointment_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    route_class=DishkaSyncRoute,
    dependencies=[Depends(oauth2_bearer)]
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
        status: Optional[str] = Query(None, description="Filter by status: pending confirmed etc"),
        has_unresolved_addons: Optional[bool] = Query(
            None, description="Only appointments with (true) or without (false) Unresolved Add-ons")):
    """Get all appointments for the currently loggedin user for business"""
    return appointment_service.get_appointments_by_business(
        current_user=current_user,
        business_id=business_id,
        has_unresolved_addons=has_unresolved_addons,
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
        appointment_id = appointment_id,
        appointment=appointment_data,
    )

@appointment_router.post("/business/{business_id}/appointments/{appointment_id}/addons", response_model=AppointmentRead)
def add_appointment_addon(business_id: int, appointment_id: int, data: AppointmentAddonCreate,
                          service: FromDishka[AppointmentAddonService], current_user: FromDishka[User]):
    """Add an Add-on to an appointment. Allowed until the appointment is completed, canceled or refunded."""
    return service.add_addon(business_id, appointment_id, data.addon_id, data.quantity, current_user)

@appointment_router.patch("/business/{business_id}/appointments/{appointment_id}/addons/{addon_id}", response_model=AppointmentRead)
def change_appointment_addon_quantity(business_id: int, appointment_id: int, addon_id: int,
                                      data: AppointmentAddonQuantityUpdate,
                                      service: FromDishka[AppointmentAddonService], current_user: FromDishka[User]):
    """Change the quantity of an Add-on already on the appointment, at its frozen unit price."""
    return service.set_quantity(business_id, appointment_id, addon_id, data.quantity, current_user)

@appointment_router.delete("/business/{business_id}/appointments/{appointment_id}/addons/{addon_id}", response_model=AppointmentRead)
def remove_appointment_addon(business_id: int, appointment_id: int, addon_id: int,
                             service: FromDishka[AppointmentAddonService], current_user: FromDishka[User]):
    """Remove an Add-on from the appointment."""
    return service.remove_addon(business_id, appointment_id, addon_id, current_user)

@appointment_router.post("/business/{business_id}/appointments/{appointment_id}/unresolved-addons/{unresolved_id}/resolve",
                         response_model=AppointmentRead)
def resolve_unresolved_addon(business_id: int, appointment_id: int, unresolved_id: int, data: UnresolvedAddonResolve,
                             service: FromDishka[AppointmentAddonService], current_user: FromDishka[User]):
    """Resolve an Unresolved Add-on by picking an Add-on from the catalogue."""
    return service.resolve_unresolved(business_id, appointment_id, unresolved_id, data.addon_id, current_user,
                                      quantity=data.quantity)

@appointment_router.post("/business/{business_id}/appointments/{appointment_id}/{event}", response_model=AppointmentRead)
def advance_appointment(business_id: int, appointment_id: int, event: AppointmentEvent,
                        service: FromDishka[AppointmentService], current_user: FromDishka[User]):
    return service.advance(business_id, appointment_id, event, current_user)

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

@appointment_router.patch("{appointment_id}/businesses/{business_id}/payments", response_model=AppointmentRead, status_code=200)
def update_appointment_payments(business_id: int, appointment_id: int):
    """Update the payments for the currently logged in user for business"""
    pass

@appointment_router.get("/businesses/{business_id}/appointments?needs_review=true", response_model=List[AppointmentRead], status_code=200)
def get_pending_review_appointments(business_id: int,needs_review: bool):
    """get all the appointments pending a review"""
    pass

