from typing import List

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.guard.jotform_guard import JotformGuard
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, SubmissionFieldDef, SUBMISSION_FIELDS
from app.domain.Jotform.port.jotform_port import JotformPort
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort
from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential, JotformFormAssignment
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.package.port.package_repository_port import PackageRepositoryPort
from app.domain.user.models.user import User




class JotformService:
    def __init__(
            self,
            business_guard: BusinessGuard,
            jotform_guard: JotformGuard,
            package_repo: PackageRepositoryPort,
            member_repo: BusinessMemberRepositoryPort,
            jotform_repo: JotformRepositoryPort,
            jotform_api: JotformPort
    ):
        self.jotform_guard = jotform_guard
        self.business_guard = business_guard
        self.member_repo = member_repo
        self.package_repo = package_repo
        self.jotform_repo = jotform_repo
        self.jotform_api = jotform_api

    def create_jotform_credential(self, data: JotformCredential, current_user: User) -> JotformCredential:
        """ Create a new jotform credential  only for admin and owner"""
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        created_jotform = JotformCredential(
            business_id=data.business_id,
            label = data.label,
            api_key = data.api_key
        )

        return self.jotform_repo.create_credential(created_jotform)

    def get_jotform_credentials(self, business_id: str, current_user: User) -> List[JotformCredential]:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)

        return self.jotform_repo.get_credential_by_business(business_id)

    def update_jotform_credentials(self, data: JotformCredential, current_user: User) -> JotformCredential:
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

        return self.jotform_repo.delete_credential(credential.id)

    def jotform_form_create(self, data: JotformForm, current_user: User) -> JotformForm:
        credential = self.jotform_guard.ensure_credential_exists(credential_id=data.credential_id)
        self.business_guard.ensure_exists(business_id=credential.business_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)

        jotform = JotformForm(
            credential_id = data.credential_id,
            form_id = data.form_id,
            name = data.name,
            field_mapping = data.field_mapping,
        )

        return self.jotform_repo.create_form(jotform)

    def get_jotform_form_by_id(self, form_id:str, current_user: User) -> JotformForm:
        jotform = self.jotform_guard.ensure_form_exists(form_id)
        credential = self.jotform_guard.ensure_credential_exists(jotform.credential_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)

        return jotform

    def get_jotform_form_by_business_id(self, business_id: int, current_user: User) -> List[JotformForm]:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        jotform = self.jotform_repo.get_forms_by_business_id(business_id)
        return jotform

    def get_jotform_form_by_member_and_category(self, business_id:int, member_id:int, category_id:int, current_user: User) -> JotformForm:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        jotform = self.jotform_repo.get_form_by_category_and_member( member_id=member_id, category_id=category_id)

        if not jotform:
            raise JotformDomainError()
        return jotform

    async def get_forms_from_api_for_credential(self, credential: JotformCredential) -> List[JotformForm]:
        result = await self.jotform_api.get_list_forms(credential.api_key)
        return result

    async def update_jotform_form_list(self, business_id: int, current_user: User) -> List[JotformForm]:
        """Update the jotform form returning the new created form"""
        self.business_guard.ensure_exists(business_id=business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        credential_list = self.get_jotform_credentials(business_id=business_id, current_user=current_user)

        result_list = []

        for credential in credential_list:
            existing_ids = {f.form_id for f in self.jotform_repo.get_forms_by_business_id(credential.business_id)}
            forms = await self.get_forms_from_api_for_credential(credential)

            for form in forms:
                if form.form_id in existing_ids:
                    continue

                form.credential_id = credential.id
                result_list.append(self.jotform_repo.create_form(form))

        return result_list

    def update_jotform_form(self, form_data: JotformForm, current_user: User) -> JotformForm:
        form = self.jotform_guard.ensure_form_exists(form_data.id)
        credential = self.jotform_guard.ensure_credential_exists(form_data.credential_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)

        form.name = form_data.name
        form.member_assigns = form_data.member_assigns
        form.field_mapping = form_data.field_mapping
        self.jotform_repo.update_form(form)
        return form


    def delete_jotform_form(self, form_id: int, current_user: User) -> bool:
        form = self.jotform_guard.ensure_form_exists(form_id)
        credential = self.jotform_guard.ensure_credential_exists(form.credential_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)
        return self.jotform_repo.delete_form(form)

    def get_jotform_list_for_credential(self, credential_id, current_user):
        """Check that credential exist , Check that the user is admin or owner of the credential id business """
        credential = self.jotform_guard.ensure_credential_exists(credential_id= credential_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)
        return self.jotform_repo.get_form_by_credential_id(credential_id)

    def assign_jotform_form_to_member_and_category(self, jotform_assignment: JotformFormAssignment, current_user: User) -> JotformForm:
        form = self.jotform_guard.ensure_form_exists(jotform_assignment.form_id)
        self.jotform_guard.ensure_jotform_assignment_doesnt_exist(category_id=jotform_assignment.category_id, form_id=jotform_assignment.form_id, business_member_id=jotform_assignment.business_member_id)
        cred = self.jotform_guard.ensure_credential_exists(form.credential_id)
        self.business_guard.ensure_admin_or_owner(cred.business_id, current_user.id)

        assignment = JotformFormAssignment(
            business_member_id=jotform_assignment.business_member_id,
            form_id=jotform_assignment.form_id,
            category_id=jotform_assignment.category_id,
        )
        return self.jotform_repo.create_assignment(assignment)

    def get_submission_field_defs(self) -> List[SubmissionFieldDef]:
        return SUBMISSION_FIELDS
    def save_field_mappings(self, form_id: int, mappings: list[JotformFieldMapping], current_user: User) -> list[
        JotformFieldMapping]:
        form = self.jotform_guard.ensure_form_exists(form_id)
        print("Saving mappings")
        credential = self.jotform_guard.ensure_credential_exists(form.credential_id)
        print("Saving mappings")
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)
        print("Saving mappings")
        self.jotform_guard.ensure_mapping_valid(mappings)
        self.jotform_guard.ensure_no_duplicate_qid(form_id=form_id, mappings=mappings)
        print("Saving mappings")
        normalized = [
            JotformFieldMapping(
                form_id=form_id,
                target_key=m.target_key,
                qid=m.qid,
                subkey=m.subkey,
                priority=m.priority,
            )
            for m in mappings
        ]
        return self.jotform_repo.set_field_mappings(form_id, normalized)

    def get_field_mappings(self, form_id: int, current_user: User) -> list[JotformFieldMapping]:
        print("Getting field mappings")
        form = self.jotform_guard.ensure_form_exists(form_id)
        credential = self.jotform_guard.ensure_credential_exists(form.credential_id)
        self.business_guard.ensure_admin_or_owner(credential.business_id, current_user.id)
        print("Getting field mappings")
        return self.jotform_repo.get_field_mappings(form_id)

    def resolve_submission(self, form: JotformForm, raw_answers: dict) -> dict:
        mappings = self.jotform_repo.get_field_mappings(form.id)

        by_key: dict[str, list[JotformFieldMapping]] = {}
        for m in mappings:
            by_key.setdefault(m.target_key, []).append(m)

        print(f"Resolving submission for mapping {mappings} by key {by_key}")
        resolved: dict = {}
        for field in SUBMISSION_FIELDS:
            value = None
            print(f"Process field {field} with rawAnswer {raw_answers}")
            for m in sorted(by_key.get(field.key, []), key=lambda m: m.priority):
                print(f"Process m {m} with rawAnswer {raw_answers}")
                raw = raw_answers.get(m.qid, {}).get("answer")
                if m.subkey and isinstance(raw, dict):
                    raw = raw.get(m.subkey)
                if raw not in (None, "", []):
                    value = raw
                    break

            if field.required and value is None:
                raise JotformDomainError()

            resolved[field.key] = value

        return resolved


