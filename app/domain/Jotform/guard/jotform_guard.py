from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, SUBMISSION_FIELD_KEYS
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort
from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential


class JotformGuard:
    def __init__(self, jotform_repo: JotformRepositoryPort) -> None:
        self.jotform_repo = jotform_repo

    def ensure_credential_exists(self, credential_id: int) -> JotformCredential:
        credential = self.jotform_repo.get_credential_by_id(credential_id)
        if not credential:
            raise JotformDomainError()
        return credential

    def ensure_credential_belongs_to_business(self, credential_id: int, business_id: int) -> JotformCredential:
        credential = self.ensure_credential_exists(credential_id)
        if credential.business_id != business_id:
            raise JotformDomainError()
        return credential

    def ensure_form_exists(self, form_id: int) -> JotformForm:
        form = self.jotform_repo.get_form_by_id(form_id)
        if not form:
            raise JotformDomainError()
        return form

    def ensure_form_belongs_to_business(self, form_id: int, business_id: int) -> JotformForm:
        form = self.ensure_form_exists(form_id)
        credential = self.ensure_credential_exists(credential_id=form.credential_id)
        if credential.business_id != business_id:
            raise JotformDomainError()
        return form

    def ensure_category_not_already_mapped(self, business_id: int, category_id: int) -> None:
        """One form = one mapping: block a second form claiming the same category."""
        existing = self.jotform_repo.get_form_by_category_id(category_id)
        if existing:
            raise JotformDomainError()

    def ensure_webhook_token_valid(self, token: str) -> JotformForm:
        """Runtime entry point — resolves the token straight to its mapping row."""
        form = self.jotform_repo.get_form_by_webhook_token(token)
        if not form:
            raise JotformDomainError()
        return form

    def ensure_jotform_assignment_doesnt_exist(self, category_id: int, business_member_id: int, form_id: int) -> None:
        form_assignments = self.jotform_repo.get_assignments_for_form(form_id)
        for assignment in form_assignments:
            if (assignment.business_member_id == business_member_id
                and assignment.form_id == form_id
                and assignment.category_id == category_id):
                raise JotformDomainError()

    def ensure_mapping_valid(self, mappings: list[JotformFieldMapping]) -> None:
        for m in mappings:
            if m.target_key not in SUBMISSION_FIELD_KEYS:
                raise JotformDomainError()

    def ensure_no_duplicate_qid(self, form_id: int, mappings: list[JotformFieldMapping]) -> None:
        seen_qids = set()
        for m in mappings:
            key = (m.qid, m.subkey)
            if key in seen_qids:
                raise JotformDomainError()
            seen_qids.add(key)

        # same target_key + priority collision (belt and suspenders on top of the DB constraint)
        seen_priority = set()
        for m in mappings:
            pk = (m.target_key, m.priority)
            if pk in seen_priority:
                raise JotformDomainError()
            seen_priority.add(pk)
