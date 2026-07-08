from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class MemberCommission(SQLModel, table = True):
    __tablename__ = "member_commission"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_member_id: int = Field(default=None, foreign_key="business_members.id")
    package_id: int = Field(default=None, foreign_key="package.id")
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime