from typing import List, Optional

from sqlmodel import Session, select

from app.db.models.Jotform.jotform import JotformCredential, JotformForm
from app.services.business.BusinessGuard import BusinessGuard


class JotformRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_credential(self, credential: JotformCredential) -> JotformCredential:
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def get_credential_by_id(self, credential_id: int) -> Optional[JotformCredential]:
        return self.db.get(JotformCredential, credential_id)

    def get_credentials_by_business(self, business_id: int) -> List[JotformCredential]:
        return self.db.exec(
            select(JotformCredential).where(JotformCredential.business_id == business_id)
        ).all()

    def delete_credential(self, credential_id: int) -> bool:
        credential = self.db.get(JotformCredential, credential_id)
        if not credential:
            return False
        self.db.delete(credential)
        self.db.commit()
        return True

    def update_credential(self, credential: JotformCredential) -> JotformCredential:
        existing = self.db.get(JotformCredential, credential.id)
        if not existing:
            return None
        for key, value in credential.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    # --- Forms (mapping lives here) ---
    def create_form(self, form: JotformForm) -> JotformForm:
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def get_form_by_id(self, form_id: int) -> Optional[JotformForm]:
        return self.db.get(JotformForm, form_id)

    def get_form_by_webhook_token(self, token: str) -> Optional[JotformForm]:
        """Runtime lookup — the only query the webhook processor needs."""
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.webhook_token == token)
            .where(JotformForm.is_active == True)
        ).first()

    def get_forms_by_business(self, business_id: int) -> List[JotformForm]:
        return self.db.exec(
            select(JotformForm).where(JotformForm.business_id == business_id)
        ).all()

    def get_form_by_category(self, business_id: int, category_id: int) -> Optional[JotformForm]:
        """Guard uses this before creating a duplicate mapping."""
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.business_id == business_id)
            .where(JotformForm.category_id == category_id)
            .where(JotformForm.is_active == True)
        ).first()

    def get_form_by_category_and_member(self, business_id: int, category_id: int, member_id: int) -> Optional[JotformForm]:
        """Guard uses this before creating a duplicate mapping."""
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.business_id == business_id)
            .where(JotformForm.category_id == category_id)
            .where(JotformForm.member_assigns == member_id)
            .where(JotformForm.is_active == True)
        ).first()

    def update_form(self, form: JotformForm) -> Optional[JotformForm]:
        existing = self.db.get(JotformForm, form.id)
        if not existing:
            return None
        for key, value in form.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete_form(self, form_id: int) -> bool:
        form = self.db.get(JotformForm, form_id)
        if not form:
            return False
        self.db.delete(form)
        self.db.commit()
        return True

