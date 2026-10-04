from datetime import datetime

from pydantic import BaseModel


class AddonPriceCreate(BaseModel):
    addon_id: int
    price: int
    effective_from: datetime


class AddonPriceRead(BaseModel):
    id: int
    addon_id: int
    price: int
    effective_from: datetime
