from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaSyncRoute
from fastapi import APIRouter, Depends

from app.api.models.addon.addon_model import AddonCreate, AddonRead, AddonUpdate
from app.api.models.addon.addon_commission_model import (
    AddonCommissionCreate, AddonCommissionRead, AddonCommissionUpdate)
from app.api.models.addon.addon_price_model import AddonPriceCreate, AddonPriceRead
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.addon.models.addon_price import AddonPrice
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
    """List the add-ons of a business: every member sees the active ones, owner and admin all of them"""
    return service.list(business_id=business_id, current_user=current_user)


@addon_router.get("/{business_id}/members/{member_id}/addon-commissions", response_model=List[AddonCommissionRead])
def list_member_addon_commissions(business_id: int, member_id: int, service: FromDishka[AddonService],
                                  current_user: FromDishka[User]):
    """The member's commission in effect on every active add-on, a flat 0 where there is no row. Owner and admin only."""
    return service.list_member_addon_commissions(
        business_id=business_id, member_id=member_id, current_user=current_user)


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


@addon_router.post("/addons/prices", response_model=AddonPriceRead, status_code=201)
def create_addon_price(data: AddonPriceCreate, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """Add a price version to an add-on, owner and admin only"""
    return service.create_price(data=AddonPrice(**data.model_dump()), current_user=current_user)


@addon_router.get("/addons/{addon_id}/prices", response_model=List[AddonPriceRead])
def get_addon_price_history(addon_id: int, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """Every price version of the add-on, newest first"""
    return service.get_price_history(addon_id=addon_id, current_user=current_user)


@addon_router.get("/addons/{addon_id}/prices/current", response_model=AddonPriceRead)
def get_addon_current_price(addon_id: int, service: FromDishka[AddonService], current_user: FromDishka[User]):
    """The price in effect now. 400 when the add-on has no price in effect."""
    return service.get_current_price(addon_id=addon_id, current_user=current_user)


@addon_router.post("/addons/commissions", response_model=AddonCommissionRead, status_code=201)
def create_addon_commission(data: AddonCommissionCreate, service: FromDishka[AddonService],
                            current_user: FromDishka[User]):
    """Set a member's commission on an add-on (percentage or flat), owner and admin only"""
    return service.create_commission(data=AddonCommission(**data.model_dump()), current_user=current_user)


@addon_router.patch("/addons/commissions", response_model=AddonCommissionRead)
def correct_addon_commission(data: AddonCommissionUpdate, service: FromDishka[AddonService],
                             current_user: FromDishka[User]):
    """Fix a commission version in place instead of adding a new dated one, owner and admin only"""
    return service.correct_commission(
        commission_id=data.id, commission_amount=data.commission_amount,
        commission_isPercentage=data.commission_isPercentage, current_user=current_user)


@addon_router.get("/addons/{addon_id}/members/{member_id}/commission", response_model=AddonCommissionRead)
def get_member_addon_commission(addon_id: int, member_id: int, service: FromDishka[AddonService],
                                current_user: FromDishka[User]):
    """The member's commission in effect on the add-on. A flat 0 when the member has no row."""
    return service.get_current_commission(member_id=member_id, addon_id=addon_id, current_user=current_user)
