from typing import List, Optional

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
    def is_owner_or_admin(self, business_id: int, user_id: int) -> bool:
        member = self.get_member(business_id, user_id)
        return bool(member and member.role in [MemberRole.OWNER, MemberRole.ADMIN])
