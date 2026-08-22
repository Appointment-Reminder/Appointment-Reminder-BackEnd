from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PackageCategory:
    id: Optional[int]
    business_id: int
    name: str

