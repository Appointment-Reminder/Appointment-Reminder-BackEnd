from typing import List

from fastapi import HTTPException

from app.db.models.Jotform.jotform import JotformCredential, JotformForm
from app.db.models.user import User
from app.models.Jotform.jotform_model import JotformCredentialCreate, JotformFormCreate, JotformFormRead, \
    JotformFormUpdate, JotformCredentialRead, JotformCredentialUpdate
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.jotform.jotform_repository import JotformRepository
from app.repositories.packages.packages_repository import PackagesRepository
from app.services.business.BusinessGuard import BusinessGuard
from app.services.jotform.jotform_guard import JotformGuard


class JotformService:
    def __init__(
            self,
            business_guard: BusinessGuard,
            jotform_guard: JotformGuard,
            package_repo: PackagesRepository,
            member_repo: BusinessMemberRepository,
            jotform_repo: JotformRepository
    ):
        self.jotform_guard = jotform_guard
        self.business_guard = business_guard
        self.member_repo = member_repo
        self.package_repo = package_repo
        self.jotform_repo = jotform_repo

    def create_jotform_credential(self, data: JotformCredentialCreate, current_user: User) -> JotformCredential:
        """ Create a new jotform credential  only for admin and owner"""
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        created_jotform = JotformCredential(
            business_id=data.business_id,
            label = data.label,
            api_key = data.api_key
        )

        return self.jotform_repo.create_credential(created_jotform)

    def get_jotform_credentials(self, business_id: str, current_user: User) -> List[JotformCredentialRead]:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)

        self.jotform_repo.get_credential_by_business_id(business_id)

    def update_jotform_credentials(self, data: JotformCredentialUpdate, current_user: User) -> JotformCredential:
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)
        credential = self.jotform_guard.ensure_credential_exists(data.id)

        credential.label = data.label
        credential.api_key = data.api_key

        self.jotform_repo.update_credential(credential)

    def delete_jotform_credentials(self, credential_id: str, current_user: User):
        credential = self.jotform_guard.ensure_credential_exists(credential_id)

        self.business_guard.ensure_exists(credential.business_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)

        self.jotform_repo.delete_credential(credential)



    def jotform_form_create(self, data: JotformFormCreate, current_user: User) -> JotformFormCreate:
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        jotform = JotformForm(
            credential_id = data.credential_id,
            business_id = data.business_id,
            category_id = data.category_id,
            form_id = data.form_id,
            name = data.name,
            member_assigns = data.member_assigns,
            field_mapping = data.field_mapping,
        )

        return self.jotform_repo.create_form(jotform)

    def get_jotform_form_by_id(self, form_id:str, current_user: User) -> JotformFormRead:
        jotform = self.jotform_guard.ensure_form_exists(form_id)
        self.business_guard.ensure_admin_or_owner(jotform.business_id, current_user.id)

        return jotform

    def get_jotform_form_by_business_id(self, business_id: int, current_user: User) -> List[JotformFormRead]:
        self.business_guard.ensure_exists(business_id)
        jotform = self.jotform_repo.get_forms_by_business(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)

        return jotform

    def get_jotform_form_by_member_and_category(self, business_id:int, member_id:int, category_id:int, current_user: User) -> JotformFormRead:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        jotform = self.jotform_repo.get_form_by_category_and_member(business_id=business_id, member_id=member_id, category_id=category_id)

        if not jotform:
            raise HTTPException(
                status_code=400,
                detail=f"jotform for not found"
            )
        return jotform

    def update_jotform_form(self, form_data: JotformFormUpdate, current_user: User) -> JotformFormRead:
        form = self.jotform_guard.ensure_form_exists(form_data.id)
        self.business_guard.ensure_admin_or_owner(form.business_id, current_user.id)

        form.name = form_data.name
        form.member_assigns = form_data.member_assigns
        form.field_mapping = form_data.field_mapping
        self.jotform_repo.update_form(form)
        return form


    def delete_jotform_form(self, form_id: int, current_user: User) -> bool:
        form = self.jotform_guard.ensure_form_exists(form_id)
        self.business_guard.ensure_admin_or_owner(form.business_id, current_user.id)
        return self.jotform_repo.delete_form(form)
