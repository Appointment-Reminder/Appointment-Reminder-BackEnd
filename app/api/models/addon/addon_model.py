from typing import Optional

from pydantic import BaseModel


class AddonCreate(BaseModel):
    business_id: int
    name: str
    jotform_alias: str
    category_id: Optional[int] = None
    has_duration: bool = False
    has_quantity: bool = False
    duration_minutes: Optional[int] = None


class AddonUpdate(BaseModel):
    name: str
    jotform_alias: str
    is_active: bool = True
    category_id: Optional[int] = None
    has_duration: bool = False
    has_quantity: bool = False
    duration_minutes: Optional[int] = None


class AddonRead(BaseModel):
    id: int
    business_id: int
    name: str
    jotform_alias: str
    is_active: bool
    category_id: Optional[int]
    has_duration: bool
    has_quantity: bool
    duration_minutes: Optional[int]
    current_price: Optional[int] = None
