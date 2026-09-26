from dataclasses import dataclass
from typing import Optional


@dataclass
class Package:
    business_id: int
    category_id: int
    name: str
    description: str
    is_active: bool

    jotform_alias: str
    package_duration: Optional[int] = None
    id: Optional[int] = None