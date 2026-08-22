from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PackagePrice:
    id: Optional[int]
    package_id: int
    total_price: int
    deposit_amount: int
    remaining_amount: int
    is_personal: bool
    effective_from: datetime
