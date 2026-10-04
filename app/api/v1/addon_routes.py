from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaSyncRoute
from fastapi import APIRouter, Depends

from app.api.models.addon.addon_model import AddonCreate, AddonRead, AddonUpdate
from app.domain.addon.models.addon import Addon
from app.domain.addon.service.addon_service import AddonService
from app.domain.user.models.user import User
from app.domain.user.service.user_service import oauth2_bearer

addon_router = APIRouter(
    prefix="/business",
    route_class=DishkaSyncRoute,
    dependencies=[Depends(oauth2_bearer)],
    tags=["business - addon"],
)


@addon_router.post("/addons", response_model=AddonRead, status_code=201)
def create_addon(data: AddonCreate, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """Create an add-on for a business, owner and admin only"""
    return service.create(data=Addon(**data.model_dump()), current_user=current_user)


@addon_router.get("/{business_id}/addons", response_model=List[AddonRead])
def list_addons(business_id: int, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """List the add-ons of a business, owner and admin only"""
    return service.list(business_id=business_id, current_user=current_user)


@addon_router.get("/addons/{addon_id}", response_model=AddonRead)
def get_addon(addon_id: int, service: FromDishka[AddonService], current_user: FromDishka[User]):
    return service.get(addon_id=addon_id, current_user=current_user)


@addon_router.put("/addons/{addon_id}", response_model=AddonRead)
def update_addon(addon_id: int, data: AddonUpdate, service: FromDishka[AddonService],
                 current_user: FromDishka[User]):
    """Update an add-on, owner and admin only"""
    return service.update(data=Addon(id=addon_id, business_id=0, **data.model_dump()), current_user=current_user)


@addon_router.post("/addons/{addon_id}/deactivate", response_model=AddonRead)
def deactivate_addon(addon_id: int, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """Deactivate an add-on. Add-ons are never hard deleted."""
    return service.deactivate(addon_id=addon_id, current_user=current_user)
