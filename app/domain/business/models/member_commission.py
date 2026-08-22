import datetime
from dataclasses import dataclass

@dataclass(frozen= True)
class MemberCommission:
    id: int
    business_member_id: int
    package_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime