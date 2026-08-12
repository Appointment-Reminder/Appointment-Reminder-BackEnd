from typing import List

from app.db.models.Jotform.jotform import JotformCredential
from app.db.models.user import User
from app.models.Jotform.jotform_model import JotformCredentialCreate, JotformFormCreate, JotformFormRead, \
    JotformFormUpdate
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.packages.packages_repository import PackagesRepository
from app.services.business.BusinessGuard import BusinessGuard
from app.services.jotform.jotform_guard import JotformGuard
from app.services.package.package_guard import PackageGuard


class JotformService:
    def __init__(
            self,
            business_guard: BusinessGuard,
            packages_guard: PackageGuard,
            jotform_guard: JotformGuard,
            package_repo: PackagesRepository,
            member_repo: BusinessMemberRepository,
    ):
        self.jotform_guard = jotform_guard
        self.packages_guard = packages_guard
        self.business_guard = business_guard
        self.member_repo = member_repo
        self.package_repo = package_repo

    def create_jotform_credential(self, data: JotformCredentialCreate, current_user: User) -> JotformCredential:
        """ Create a new jotform credential  only for admin and owner"""
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)


        ...

    def get_jotform_credentials(self, business_id: str, current_user: User) -> List[JotformCredential]:
        ...

    def update_jotform_credentials(self, data: JotformCredentialCreate, current_user: User) -> JotformCredential:
        ...

    def delete_jotform_credentials(self, credential_id: str, current_user: User):
        ...

    def jotform_form_create(self, data: JotformFormCreate, current_user: User) -> JotformFormCreate:
        ...

    def get_jotform_form_by_id(self, form_id:str, current_user: User) -> JotformFormRead:
        ...

    def get_jotform_form_by_business_id(self, business_id: int, current_user: User) -> List[JotformFormRead]:
        ...

    def get_jotform_form_by_member_and_category(self, member_id:str, category_id:str, current_user: User) -> JotformFormRead:
        ...

    def update_jotform_form(self, form_data: JotformFormUpdate, current_user: User) -> JotformFormRead:
        ...

    def delete_jotform_form(self, form_id: str, current_user: User) -> bool:
        ...