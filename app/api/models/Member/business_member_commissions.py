from datetime import datetime

from pydantic import BaseModel


class BusinessMemberCommissionsCreate(BaseModel):
    business_member_id: int
    package_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime

class BusinessMemberCommissionsRead(BaseModel):
    id: int
    business_member_id: int
    package_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime

class BusinessMemberCommissionsUpdate(BaseModel):
    id: int
    commission_amount: int
    commission_isPercentage: bool