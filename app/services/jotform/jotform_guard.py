from fastapi import HTTPException

from app.repositories.jotform.jotform_repository import JotformRepository
from app.db.models.Jotform.jotform import JotformCredential, JotformForm


class JotformGuard:
    def __init__(self, jotform_repo: JotformRepository) -> None:
        self.jotform_repo = jotform_repo

    def ensure_credential_exists(self, credential_id: int) -> JotformCredential:
        credential = self.jotform_repo.get_credential_by_id(credential_id)
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        return credential

    def ensure_credential_belongs_to_business(self, credential_id: int, business_id: int) -> JotformCredential:
        credential = self.ensure_credential_exists(credential_id)
        if credential.business_id != business_id:
            raise HTTPException(status_code=403, detail="This credential does not belong to this business")
        return credential

    def ensure_form_exists(self, form_id: int) -> JotformForm:
        form = self.jotform_repo.get_form_by_id(form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Jotform mapping not found")
        return form

    def ensure_form_belongs_to_business(self, form_id: int, business_id: int) -> JotformForm:
        form = self.ensure_form_exists(form_id)
        if form.business_id != business_id:
            raise HTTPException(status_code=403, detail="This mapping does not belong to this business")
        return form

    def ensure_category_not_already_mapped(self, business_id: int, category_id: int) -> None:
        """One form = one mapping: block a second form claiming the same category."""
        existing = self.jotform_repo.get_form_by_category(business_id, category_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Category {category_id} is already mapped to another form"
            )

    def ensure_webhook_token_valid(self, token: str) -> JotformForm:
        """Runtime entry point — resolves the token straight to its mapping row."""
        form = self.jotform_repo.get_form_by_webhook_token(token)
        if not form:
            raise HTTPException(status_code=404, detail="Invalid or inactive webhook token")
        return form
