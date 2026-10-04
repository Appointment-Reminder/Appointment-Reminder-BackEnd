from dataclasses import dataclass
from typing import Optional


@dataclass
class Addon:
    business_id: int
    name: str
    jotform_alias: str
    is_active: bool = True
    category_id: Optional[int] = None
    has_duration: bool = False
    has_quantity: bool = False
    duration_minutes: Optional[int] = None
    id: Optional[int] = None
    current_price: Optional[int] = None  # read-side only, never stored
