from typing import Optional, List

from sqlmodel import select, Session

from app.domain.Jotform.models.jotform_form_model import JotformForm as JotformFormEntity, JotformCredential as JotformCredentialEntity
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort

from app.adapters.sql_model_adapter.jotform.models.jotform import JotformCredential as JotformCredentialSQL, JotformForm as JotformFormSQL
from app.adapters.sql_model_adapter.jotform.models.jotform import jotform_credential_apply_sql,jotform_credential_to_domain, jotform_form_apply_sql, jotform_form_to_domain

class SQLModelJotformRepositoryAdapter(JotformRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db
    def create_credential(self, credential: JotformCredentialEntity) -> JotformCredentialEntity:
        sql_obj = JotformCredentialSQL(
            business_id=credential.business_id,
            label=credential.label,
            api_key=credential.api_key,
            created_at=credential.created_at,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return jotform_credential_to_domain(sql_obj)

    def get_credential_by_id(self, credential_id: int) -> Optional[JotformCredentialEntity]:
        result = self.db.get(JotformCredentialSQL, credential_id)
        return jotform_credential_to_domain(result) if result else None

    def get_credential_by_business(self, business_id: int) -> List[JotformCredentialEntity]:
        result = self.db.exec(
            select(JotformCredentialSQL).where(JotformCredentialSQL.business_id == business_id)
        ).all()

        return [jotform_credential_to_domain(item) for item in result]

    def update_credential(self, credential: JotformCredentialEntity) -> JotformCredentialEntity:
        existing = self.db.get(JotformCredentialSQL, credential.id)
        if not existing:
            return None
        jotform_credential_apply_sql(sql=existing, obj=credential)
        self.db.commit()
        self.db.refresh(existing)
        return jotform_credential_to_domain(existing)
    def delete_credential(self, credential_id: int) -> bool:
        credential = self.db.get(JotformCredentialSQL, credential_id)
        if not credential:
            return False
        self.db.delete(credential)
        self.db.commit()
        return True

    def create_form(self, form: JotformFormEntity) -> JotformFormEntity:
        sql_obj = JotformFormSQL(
            credential_id=form.credential_id,
            category_id=form.category_id,
            form_id=form.form_id,
            name=form.name,
            member_assigns=form.member_assigns,
            field_mapping=form.field_mapping,
            is_active=form.is_active,
            webhook_token=form.webhook_token,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return jotform_form_to_domain(sql_obj)

    def get_form_by_id(self, jotform_id: int) -> JotformFormEntity:
        result = self.db.get(JotformFormSQL, jotform_id)
        return jotform_form_to_domain(result) if result else None

    def get_form_by_webhook_token(self, webhook_token: str) -> JotformFormEntity:
        result = self.db.exec(
            select(JotformFormSQL)
            .where(JotformFormSQL.webhook_token == webhook_token)
            .where(JotformFormSQL.is_active == True)
        ).first()

        return jotform_form_to_domain(result)

    def get_form_by_business_id(self, business_id: int) -> List[JotformFormEntity]:
        result = self.db.exec(
            select(JotformFormSQL).where(JotformFormSQL.business_id == business_id)
        ).all()

        return [jotform_form_to_domain(item) for item in result]

    def get_form_by_category_id(self, category_id: int) -> JotformFormEntity:
        result = self.db.exec(
            select(JotformFormSQL)
            .where(JotformFormSQL.category_id == category_id)
            .where(JotformFormSQL.is_active == True)
        ).first()
        return jotform_form_to_domain(result)

    def get_form_by_category_and_member(self, category_id: int, member_id: int) -> JotformFormEntity:
        result = self.db.exec(
            select(JotformFormSQL)
            .where(JotformFormSQL.category_id == category_id)
            .where(JotformFormSQL.member_assigns == member_id)
            .where(JotformFormSQL.is_active == True)
        ).first()

        return jotform_form_to_domain(result)

    def update_form(self, form: JotformFormEntity) -> JotformFormEntity:
        existing = self.db.get(JotformFormSQL, form.id)
        if not existing:
            return None

        jotform_form_apply_sql(sql=existing, obj=form)

        self.db.commit()
        self.db.refresh(existing)
        return jotform_form_to_domain(existing)

    def delete_form(self, form: JotformFormEntity) -> bool:
        form = self.db.get(JotformFormSQL, form.id)
        if not form:
            return False
        self.db.delete(form)
        self.db.commit()
        return True