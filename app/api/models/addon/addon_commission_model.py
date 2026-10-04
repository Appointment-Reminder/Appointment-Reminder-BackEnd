from datetime import datetime

from pydantic import BaseModel


class AddonCommissionCreate(BaseModel):
    business_member_id: int
    addon_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime


class AddonCommissionRead(BaseModel):
    id: int | None = None
    business_member_id: int
    addon_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime
