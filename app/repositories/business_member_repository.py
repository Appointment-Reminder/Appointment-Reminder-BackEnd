from typing import List, Optional

from pyasn1.type.univ import Boolean
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db.models.business_member import BusinessMember, MemberRole


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

