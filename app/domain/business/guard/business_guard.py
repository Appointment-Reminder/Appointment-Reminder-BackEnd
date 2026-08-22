from app.domain.business.errors.business_errors import InvalidBusiness, BusinessError
from app.domain.business.models.business_member_model import BusinessMember, MemberRole
from app.domain.business.models.business_model import Business
from app.domain.business.models.member_commission import MemberCommission
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.business.port.business_repository_port import BusinessRepositoryPort


class BusinessGuard:
    def __init__(
            self,
            business_repo: BusinessRepositoryPort,
            business_member_repo: BusinessMemberRepositoryPort,
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
            raise BusinessError()
        return member

    def ensure_is_a_member(self, business_id: int, user_id:int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if not member:
            raise BusinessError()
        return member

    def ensure_not_a_member(self, business_id: int, user_id: int):
        member = self.business_member_repo.get_member(business_id, user_id)
        if member:
            raise BusinessError()
        return

    def ensure_admin_or_owner(self, business_id: int, user_id: int) -> BusinessMember:
        member = self.business_member_repo.get_member(business_id, user_id)
        if member.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
            raise BusinessError()
        return member

    def ensure_commission_Exist(self, commission_id: int) -> MemberCommission:
        commission = self.business_member_repo.get_commission_by_id(commission_id=commission_id)
        if not commission:
            raise BusinessError()

        print(f'commission found {commission}')
        return commission

"""
    def ensure_form_Exist(self, form_id: int) -> BusinessMemberForm:
        print(f"ensure form exist: {form_id}")
        form = self.business_member_repo.get_form(form_id)
        if not form:
            raise BusinessError()
        return form
"""


