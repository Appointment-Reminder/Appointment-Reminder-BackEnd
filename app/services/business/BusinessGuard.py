from fastapi import HTTPException

from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.db.models.business import Business
from app.db.models.business_member import BusinessMember, MemberRole
from app.services.errors.BusinessErrors import UserNotFoundInBusiness, UnauthorizedBusinessAction, InvalidBusiness
from app.db.models.Member.business_member_form import BusinessMemberForm
from app.db.models.Member.member_commision import MemberCommission


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
            raise InvalidBusiness(business_id=business_id)
        return business

    def ensure_member_exist(self, member_id) -> BusinessMember:
        member = self.business_member_repo.get_member_by_id( member_id=member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    def ensure_is_a_member(self, business_id: int, user_id:int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if not member:
            raise UserNotFoundInBusiness(user_id=user_id, business_id=business_id)
        return member

    def ensure_not_a_member(self, business_id: int, user_id: int):
        member = self.business_member_repo.get_member(business_id, user_id)
        if member:
            raise UserNotFoundInBusiness(user_id=user_id, business_id=business_id)
        return

    def ensure_admin_or_owner(self, business_id: int, user_id: int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if member.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
            raise UnauthorizedBusinessAction(user_id=user_id, business_id=business_id)
        return member

    def ensure_form_Exist(self, form_id: int) -> BusinessMemberForm:
        print(f"ensure form exist: {form_id}")
        form = self.business_member_repo.get_form(form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        return form

    def ensure_commission_Exist(self, commission_id: int) -> MemberCommission:
        commission = self.business_member_repo.get_commission_by_id(commission_id=commission_id)
        if not commission:
            raise HTTPException(status_code=404, detail="Commission not found")

        print(f'commission found {commission}')
        return commission
