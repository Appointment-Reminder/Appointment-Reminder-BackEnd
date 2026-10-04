from datetime import date
from typing import Literal, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaSyncRoute
from fastapi import APIRouter, Depends, Query

from app.api.models.overview_model import BusinessOverviewRead
from app.domain.overview.service.business_overview_service import BusinessOverviewService
from app.domain.user.models.user import User
from app.domain.user.service.user_service import oauth2_bearer

overview_router = APIRouter(
    prefix="/business",
    route_class=DishkaSyncRoute,
    dependencies=[Depends(oauth2_bearer)],
    tags=["business - overview"],
)


@overview_router.get("/{business_id}/overview", response_model=BusinessOverviewRead)
def get_business_overview(
        business_id: int,
        service: FromDishka[BusinessOverviewService],
        current_user: FromDishka[User],
        period_from: date = Query(alias="from", description="First day, in Paris time, inclusive"),
        period_to: date = Query(alias="to", description="Last day, in Paris time, inclusive"),
        group_by: Optional[Literal["day", "week", "month"]] = Query(None, description="Income per bucket"),
        member_id: Optional[int] = Query(None, description="A photographer may only ask for their own row")):
    """Results of the business and of each photographer. Owner and admin see everything (Owner Take: owner only),
    a photographer sees only their own row."""
    return service.overview(business_id=business_id, current_user=current_user, period_from=period_from,
                            period_to=period_to, group_by=group_by, member_id=member_id)
