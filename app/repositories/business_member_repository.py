from datetime import datetime
from typing import List, Optional

from pyasn1.type.univ import Boolean
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db.models.business_member import BusinessMember, MemberRole
from models.Member.business_member_form import BusinessMemberForm
from models.Member.member_commision import MemberCommission


class BusinessMemberRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, business_member: BusinessMember) -> BusinessMember:
        self.db.add(business_member)
        self.db.commit()
        self.db.refresh(business_member)
        return business_member

    def get_member(self, business_id: int, user_id: int) -> Optional[BusinessMember]:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .where(BusinessMember.user_id == user_id)
            .where(BusinessMember.is_active == True)
        ).first()

    def get_member_by_id(self, business_id: int, member_id: int) -> Optional[BusinessMember]:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .where(BusinessMember.id == member_id)
            .where(BusinessMember.is_active == True)
        ).first()

    def get_by_business_id(self, business_id: int) -> List[BusinessMember]:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.business_id == business_id)
            .options(selectinload(BusinessMember.user))
            .options(selectinload(BusinessMember.invited_by_user))
        ).all()

    def get_member_by_token(self, token:str) -> Optional[BusinessMember]:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.webhook_token == token)
        ).first()

    def is_owner_or_admin(self, business_id: int, user_id: int) -> bool:
        member = self.get_member(business_id, user_id)
        return bool(member and member.role in [MemberRole.OWNER, MemberRole.ADMIN])

    def update(self, member: BusinessMember) -> BusinessMember:
        business_member = self.db.get(BusinessMember, member.id)
        if not business_member:
            return None

        update_data = member.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(business_member, key, value)

        self.db.commit()
        self.db.refresh(business_member)
        return business_member

    def delete(self, member_id: int) -> bool:
        business_member = self.db.get(BusinessMember, member_id)

        if not business_member:
            return False

        self.db.delete(business_member)
        self.db.commit()
        return True

    ## Business member form

    def create_form(self, form: BusinessMemberForm) -> BusinessMember:
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def get_form_by_token(self, token: str) -> Optional[BusinessMemberForm]:
        return self.db.exec(
            select(BusinessMember)
            .where(BusinessMember.webhook_token == token)
            .where(BusinessMemberForm.webhook_token == True)
        ).first()

    def get_forms_for_member(self, member_id: int) -> List[BusinessMemberForm]:
        return self.db.exec(
            select(BusinessMemberForm)
            .where(BusinessMemberForm.business_member_id == member_id)
            .where(BusinessMemberForm.is_active == True)
        ).all()

    def update_form(self, form: BusinessMemberForm) -> Optional[BusinessMemberForm]:
        existing = self.db.get(BusinessMemberForm, form.id)
        if not existing:
            return None
        for key, value in form.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing
    def delete_form(self, form: BusinessMemberForm) -> BusinessMember:
        business_member = self.db.get(BusinessMemberForm, form.id)
        if not business_member:
            return False

        self.db.delete(BusinessMemberForm, form.id)
        self.db.commit()
        return True

    ##Commission
    def set_commission(self, commission: MemberCommission) -> MemberCommission:
        self.db.add(commission)
        self.db.commit()
        self.db.refresh(commission)
        return commission

    def get_commission_at_date(
        self,
        member_id: int,
        package_id: int,
        at_date: datetime
    ) -> Optional[MemberCommission]:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .where(MemberCommission.package_id == package_id)
            .where(MemberCommission.effective_from <= at_date)
            .order_by(MemberCommission.effective_from.desc())
            .limit(1)
        ).first()

    def get_current_commission(
        self,
        member_id: int,
        package_id: int
    ) -> Optional[MemberCommission]:
        return self.db.exec(
            select(MemberCommission)
            .where(MemberCommission.business_member_id == member_id)
            .where(MemberCommission.package_id == package_id)
            .order_by(MemberCommission.effective_from.desc())
            .limit(1)
        ).first()

    def get_commission_history(
        self,
        member_id: int,
        package_id: int
    ) -> List[MemberCommission]:
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

    def delete_commission(self, commission: MemberCommission) -> MemberCommission:
        commission = self.db.get(MemberCommission, commission.id)
        if not commission:
            return False

        self.db.delete(BusinessMemberForm, commission.id)
        self.db.commit()
        return True



