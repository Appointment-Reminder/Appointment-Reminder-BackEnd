from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen= True)
class MemberCommission:
    business_member_id: int
    package_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime
    id: Optional[int] = None