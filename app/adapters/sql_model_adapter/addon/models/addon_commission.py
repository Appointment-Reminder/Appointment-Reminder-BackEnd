from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.addon.models.addon_commission import AddonCommission as AddonCommissionEntity


class AddonCommission(SQLModel, table=True):
    __tablename__ = "addon_commission"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_member_id: int = Field(foreign_key="business_members.id", index=True)
    addon_id: int = Field(foreign_key="addon.id", index=True)
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime


def _to_domain(sql: AddonCommission) -> AddonCommissionEntity:
    return AddonCommissionEntity(
        id=sql.id,
        business_member_id=sql.business_member_id,
        addon_id=sql.addon_id,
        commission_amount=sql.commission_amount,
        commission_isPercentage=sql.commission_isPercentage,
        effective_from=sql.effective_from,
    )
