from datetime import datetime

from pydantic import BaseModel


class PackagePriceCreate(BaseModel):
    package_id: int
    total_price:int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime

class PackagePriceRead(BaseModel):
    id: int
    package_id: int
    total_price: int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime


class PackagePriceUpdate(BaseModel):
    id: int
    package_id: int
    total_price: int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime