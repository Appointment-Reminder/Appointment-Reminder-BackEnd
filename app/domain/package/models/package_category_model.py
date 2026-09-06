from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PackageCategory:
    business_id: int
    name: str
    id: Optional[int] = None

