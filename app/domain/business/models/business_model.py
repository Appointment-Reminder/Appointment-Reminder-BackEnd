from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Business:
    id: int
    name: str
    description: str
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
