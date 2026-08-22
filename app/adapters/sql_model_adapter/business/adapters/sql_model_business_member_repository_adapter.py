from datetime import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from app.domain.business.models.business_member_model import BusinessMember, MemberRole
from app.domain.business.models.member_commission import MemberCommission
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from models.Member.business_member_form import BusinessMemberForm


class SQLModelBusinessMemberRepositoryAdapter(BusinessMemberRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, business_member: BusinessMember) -> BusinessMember:
        self.db.add(business_member)
        self.db.commit()
        self.db.refresh(business_member)
        return business_member

    def get_member(self, business_id: int, user_id: int) -> BusinessMember:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .where(BusinessMember.user_id == user_id)
            .where(BusinessMember.is_active == True)
        ).first()

    def get_member_by_id(self, member_id: int) -> BusinessMember:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.id == member_id)
            .where(BusinessMember.is_active == True)
        ).first()

    def get_by_business_id(self, business_id: int) -> BusinessMember:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .options(selectinload(BusinessMember.user))
            .options(selectinload(BusinessMember.invited_by_user))
        ).all()

    def is_owner_or_admin(self, business_id: int, user_id: int) -> bool:
        member = self.get_member(business_id, user_id)
        return bool(member and member.role in [MemberRole.OWNER, MemberRole.ADMIN])

    def update(self, business_member: BusinessMember) -> BusinessMember:
        business_member = self.db.get(BusinessMember, business_member.id)
        if not business_member:
            return None

        update_data = business_member.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(business_member, key, value)

        self.db.commit()
        self.db.refresh(business_member)
        return business_member

    def delete(self, member_id: int) -> BusinessMember:
        business_member = self.db.get(BusinessMember, member_id)

        if not business_member:
            return False

        self.db.delete(business_member)
        self.db.commit()
        return True

    def set_commission(self, commission: MemberCommission) -> MemberCommission:
        self.db.add(commission)
        self.db.commit()
        self.db.refresh(commission)
        return commission

    def get_commission_by_id(self, commission_id: int) -> MemberCommission:
        return self.db.get(MemberCommission, commission_id)

    def get_commission(self, member_id: int) -> MemberCommission:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .order_by(MemberCommission.effective_from.desc())
            .limit(1)
        ).first()

    def get_commission_at_date(self, member_id: int, package_id: int, at_date: datetime) -> Optional[MemberCommission]:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .where(MemberCommission.package_id == package_id)
            .where(MemberCommission.effective_from <= at_date)
            .order_by(MemberCommission.effective_from.desc())
            .limit(1)
        ).first()

    def get_current_commission(self, member_id: int, package_id: int) -> Optional[MemberCommission]:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .where(MemberCommission.package_id == package_id)
            .order_by(MemberCommission.effective_from.desc())
            .limit(1)
        ).first()

    def get_current_business_commission(self, business_id: int) -> Optional[MemberCommission]:
        latest_subq = (
            select(
                MemberCommission.business_member_id,
                MemberCommission.package_id,
                func.max(MemberCommission.effective_from).label("max_effective_from")
            )
            .join(BusinessMember, MemberCommission.business_member_id == BusinessMember.id)
            .where(BusinessMember.business_id == business_id)
            .where(BusinessMember.is_active == True)
            .group_by(MemberCommission.business_member_id, MemberCommission.package_id)
            .subquery()
        )

        return self.db.exec(
            select(MemberCommission)
            .join(
                latest_subq,
                (MemberCommission.business_member_id == latest_subq.c.business_member_id)
                & (MemberCommission.package_id == latest_subq.c.package_id)
                & (MemberCommission.effective_from == latest_subq.c.max_effective_from)
            )
        ).all()

    def get_commission_history(self, member_id: int, package_id: int) -> Optional[MemberCommission]:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .where(MemberCommission.package_id == package_id)
            .order_by(MemberCommission.effective_from.desc())
        ).all()

    def update_commission(self, commission: MemberCommission) -> MemberCommission:
        existing = self.db.get(MemberCommission, commission.id)
        if not existing:
            return None
        for key, value in commission.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete_commission(self, commission_id: int) -> bool:
        commission = self.db.get(MemberCommission, commission_id)
        if not commission:
            return False

        self.db.delete(BusinessMemberForm, commission.id)
        self.db.commit()
        return True