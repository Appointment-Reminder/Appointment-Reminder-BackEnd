from sqlmodel import select, Session

from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort


class SQLModelJotformRepositoryAdapter(JotformRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db
    def create_credential(self, credential: JotformCredential) -> JotformCredential:
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def get_credential_by_id(self, credential_id: int) -> JotformCredential:
        return self.db.get(JotformCredential, credential_id)

    def get_credential_by_business(self, business_id: int) -> JotformCredential:
        return self.db.exec(
            select(JotformCredential).where(JotformCredential.business_id == business_id)
        ).all()

    def update_credential(self, credential: JotformCredential) -> JotformCredential:
        existing = self.db.get(JotformCredential, credential.id)
        if not existing:
            return None
        for key, value in credential.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing
    def delete_credential(self, credential_id: int) -> bool:
        credential = self.db.get(JotformCredential, credential_id)
        if not credential:
            return False
        self.db.delete(credential)
        self.db.commit()
        return True

    def create_form(self, form: JotformForm) -> JotformForm:
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def get_form_by_id(self, jotform_id: int) -> JotformForm:
        return self.db.get(JotformForm, jotform_id)

    def get_form_by_webhook_token(self, webhook_token: str) -> JotformForm:
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.webhook_token == webhook_token)
            .where(JotformForm.is_active == True)
        ).first()

    def get_form_by_business_id(self, business_id: int) -> JotformForm:
        return self.db.exec(
            select(JotformForm).where(JotformForm.business_id == business_id)
        ).all()

    def get_form_by_category_id(self, category_id: int) -> JotformForm:
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.category_id == category_id)
            .where(JotformForm.is_active == True)
        ).first()

    def get_form_by_category_and_member(self, category_id: int, member_id: int) -> JotformForm:
        return self.db.exec(
            select(JotformForm)
            .where(JotformForm.category_id == category_id)
            .where(JotformForm.member_assigns == member_id)
            .where(JotformForm.is_active == True)
        ).first()

    def update_form(self, form: JotformForm) -> JotformForm:
        existing = self.db.get(JotformForm, form.id)
        if not existing:
            return None
        for key, value in form.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete_form(self, form: JotformForm) -> bool:
        form = self.db.get(JotformForm, form.id)
        if not form:
            return False
        self.db.delete(form)
        self.db.commit()
        return True