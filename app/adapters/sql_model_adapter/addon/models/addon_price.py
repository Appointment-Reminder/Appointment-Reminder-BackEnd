from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.addon.models.addon_price import AddonPrice as AddonPriceEntity


class AddonPrice(SQLModel, table=True):
    __tablename__ = "addon_price"

    id: Optional[int] = Field(default=None, primary_key=True)
    addon_id: int = Field(foreign_key="addon.id", index=True)
    price: int
    effective_from: datetime


def _to_domain(sql: AddonPrice) -> AddonPriceEntity:
    return AddonPriceEntity(
        id=sql.id,
        addon_id=sql.addon_id,
        price=sql.price,
        effective_from=sql.effective_from,
    )
