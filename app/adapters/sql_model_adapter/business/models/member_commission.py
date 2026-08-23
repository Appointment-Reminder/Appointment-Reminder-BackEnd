from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


from app.domain.business.models.member_commission import MemberCommission as MemberCommissionEntity



class MemberCommission(SQLModel, table = True):
    __tablename__ = "member_commission"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_member_id: int = Field(default=None, foreign_key="business_members.id")
    package_id: int = Field(default=None, foreign_key="package.id")
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime

def _to_domain(sqlobj: MemberCommission) -> MemberCommissionEntity:
    return MemberCommissionEntity(
        id=sqlobj.id,
        business_member_id=sqlobj.business_member_id,
        package_id=sqlobj.package_id,
        commission_amount=sqlobj.commission_amount,
        commission_isPercentage=sqlobj.commission_isPercentage,
        effective_from=sqlobj.effective_from,
    )

def _apply_to_sql(sql: MemberCommission, obj: MemberCommissionEntity) -> None:
    sql.commission_amount = obj.commission_amount
    sql.commission_isPercentage = obj.commission_isPercentage