from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember as BusinessMemberSQL, \
    _to_domain as business_member_to_domain, _apply_to_sql as business_member_apply_to_sql

from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission as MemberCommissionSQL, \
    _to_domain as member_commission_to_domain,  _apply_to_sql as member_commission_apply_to_sql


from app.domain.business.models.member_commission import MemberCommission as MemberCommissionEntity

from app.domain.business.models.business_member_model import BusinessMember as BusinessMemberEntity, MemberRole

from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort



class SQLModelBusinessMemberRepositoryAdapter(BusinessMemberRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(BusinessMemberSQL).options(
            selectinload(BusinessMemberSQL.user),
            selectinload(BusinessMemberSQL.invited_by_user),
        )

    def create(self, business_member: BusinessMemberEntity) -> BusinessMemberEntity:
        sql_member = BusinessMemberSQL(
            business_id = business_member.business_id,
            user_id = business_member.user_id,
            role = business_member.role,
            invited_by = business_member.invited_by,
        )
        self.db.add(sql_member)
        self.db.commit()
        self.db.refresh(sql_member, attribute_names=["user", "invited_by_user"])
        return business_member_to_domain(sql_member)

    def get_member(self, business_id: int, user_id: int) -> BusinessMemberEntity:
        result = self.db.exec(
            self._base_query()
            .where(BusinessMemberSQL.business_id == business_id)
            .where(BusinessMemberSQL.user_id == user_id)
            .where(BusinessMemberSQL.is_active == True)
        ).first()
        return business_member_to_domain(result) if result else None

    def get_member_by_id(self, member_id: int) -> BusinessMemberEntity:
        result = self.db.exec(
            self._base_query()
            .where(BusinessMemberSQL.id == member_id)
            .where(BusinessMemberSQL.is_active == True)
        ).first()
        return business_member_to_domain(result) if result else None


    def get_by_business_id(self, business_id: int) -> BusinessMemberEntity:
        result = self.db.exec(
            self._base_query()
            .where(BusinessMemberSQL.business_id == business_id)
        ).all()
        return [ business_member_to_domain(row) for row in result ]

    def is_owner_or_admin(self, business_id: int, user_id: int) -> bool:
        member = self.get_member(business_id, user_id)
        return bool(member and member.role in [MemberRole.OWNER, MemberRole.ADMIN])

    def update(self, business_member: BusinessMemberEntity) -> BusinessMemberEntity:
        found_member = self.db.get(BusinessMemberSQL, business_member.id)
        if not found_member:
            return None

        business_member_apply_to_sql(found_member, business_member)

        self.db.commit()
        self.db.refresh(found_member)
        return business_member_to_domain(found_member)

    def delete(self, member_id: int) -> BusinessMemberEntity:
        found_member = self.db.get(BusinessMemberSQL, member_id)

        if not found_member:
            return False

        self.db.delete(found_member)
        self.db.commit()
        return True

    def set_commission(self, commission: MemberCommissionEntity) -> MemberCommissionEntity:
        sql_commission = MemberCommissionSQL(
            business_member_id = commission.business_member_id,
            package_id = commission.package_id,
            commission_amount = commission.commission_amount,
            commission_isPercentage = commission.commission_isPercentage,
            effective_from = commission.effective_from,
        )
        self.db.add(sql_commission)
        self.db.commit()
        self.db.refresh(sql_commission)
        return member_commission_to_domain(sql_commission)

    def get_commission_by_id(self, commission_id: int) -> MemberCommissionEntity:
        result =  self.db.get(MemberCommissionSQL, commission_id)
        return member_commission_to_domain(result) if result else None

    def get_commission(self, member_id: int) -> MemberCommissionEntity:
        result = self.db.exec(
            select(MemberCommissionSQL)
            .where(MemberCommissionSQL.business_member_id == member_id)
            .order_by(MemberCommissionSQL.effective_from.desc())
            .limit(1)
        ).first()
        return member_commission_to_domain(result) if result else None

    def get_commission_at_date(self, member_id: int, package_id: int, at_date: datetime) -> Optional[MemberCommissionEntity]:
        result = self.db.exec(
            select(MemberCommissionSQL)
            .where(MemberCommissionSQL.business_member_id == member_id)
            .where(MemberCommissionSQL.package_id == package_id)
            .where(MemberCommissionSQL.effective_from <= at_date)
            .order_by(MemberCommissionSQL.effective_from.desc())
            .limit(1)
        ).first()
        return member_commission_to_domain(result) if result else None

    def get_current_commission(self, member_id: int, package_id: int) -> Optional[MemberCommissionEntity]:
        result = self.db.exec(
            select(MemberCommissionSQL)
            .where(MemberCommissionSQL.business_member_id == member_id)
            .where(MemberCommissionSQL.package_id == package_id)
            .order_by(MemberCommissionSQL.effective_from.desc())
            .limit(1)
        ).first()

        return member_commission_to_domain(result) if result else None

    def get_current_business_commission(self, business_id: int) -> Optional[MemberCommissionEntity]:
        latest_subq = (
            select(
                MemberCommissionSQL.business_member_id,
                MemberCommissionSQL.package_id,
                func.max(MemberCommissionSQL.effective_from).label("max_effective_from")
            )
            .join(BusinessMemberSQL, MemberCommissionSQL.business_member_id == BusinessMemberSQL.id)
            .where(BusinessMemberSQL.business_id == business_id)
            .where(BusinessMemberSQL.is_active == True)
            .group_by(MemberCommissionSQL.business_member_id, MemberCommissionSQL.package_id)
            .subquery()
        )

        result = self.db.exec(
            select(MemberCommissionSQL)
            .join(
                latest_subq,
                (MemberCommissionSQL.business_member_id == latest_subq.c.business_member_id)
                & (MemberCommissionSQL.package_id == latest_subq.c.package_id)
                & (MemberCommissionSQL.effective_from == latest_subq.c.max_effective_from)
            )
        ).all()
        return [member_commission_to_domain(item) for item in result] if result else None

    def get_commission_history(self, member_id: int, package_id: int) -> Optional[MemberCommissionEntity]:
        result = self.db.exec(
            select(MemberCommissionSQL)
            .where(MemberCommissionSQL.business_member_id == member_id)
            .where(MemberCommissionSQL.package_id == package_id)
            .order_by(MemberCommissionSQL.effective_from.desc())
        ).all()
        return [member_commission_to_domain(item) for item in result] if result else None

    def update_commission(self, commission: MemberCommissionEntity) -> MemberCommissionEntity:
        existing = self.db.get(MemberCommissionSQL, commission.id)
        if not existing:
            return None
        member_commission_apply_to_sql(sql=existing, obj=commission)

        self.db.commit()
        self.db.refresh(existing)
        return business_member_to_domain(existing)

    def delete_commission(self, commission_id: int) -> bool:
        commission = self.db.get(MemberCommissionSQL, commission_id)
        if not commission:
            return False

        self.db.delete(commission)
        self.db.commit()
        return True