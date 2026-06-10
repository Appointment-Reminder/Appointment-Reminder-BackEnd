from fastapi import HTTPException

from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.db.models.business import Business
from app.db.models.business_member import BusinessMember, MemberRole
from app.services.errors.BusinessErrors import UserNotFoundInBusiness, UnauthorizedBusinessAction


class BusinessGuard:
    def __init__(
            self,
            business_repo: BusinessRepository,
            business_member_repo: BusinessMemberRepository
    ):
        self.business_repo = business_repo
        self.business_member_repo = business_member_repo

    def ensure_exists(self, business_id: int) -> Business:
        business = self.business_repo.find_by_id(business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        return business

    def ensure_member(self, business_id: int, user_id:int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if not member:
            raise UserNotFoundInBusiness(user_id=user_id, business_id=business_id)
        return member

    def ensure_admin_or_owner(self, business_id: int, user_id: int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if member.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
            raise UnauthorizedBusinessAction(user_id=user_id, business_id=business_id)