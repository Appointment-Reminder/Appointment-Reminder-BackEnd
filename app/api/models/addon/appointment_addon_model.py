from typing import Optional

from pydantic import BaseModel


class AppointmentAddonRead(BaseModel):
    id: int
    addon_id: int
    addon_price_id: int
    quantity: int
    unit_price: float
    unit_duration: int
    unit_commission_percent: Optional[float]
    unit_commission_amount: Optional[float]
    line_total: float
    line_commission: Optional[float]
    raw_label: Optional[str] = None

    class Config:
        from_attributes = True


class UnresolvedAddonRead(BaseModel):
    id: int
    raw_label: str

    class Config:
        from_attributes = True


class AppointmentAddonCreate(BaseModel):
    addon_id: int
    quantity: int = 1


class AppointmentAddonQuantityUpdate(BaseModel):
    quantity: int


class UnresolvedAddonResolve(BaseModel):
    addon_id: int
    quantity: int = 1
