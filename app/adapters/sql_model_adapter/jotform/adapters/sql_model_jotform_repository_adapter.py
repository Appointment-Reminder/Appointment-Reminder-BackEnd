from typing import Optional, List

from sqlmodel import select, Session
from urllib3.util import url

from app.domain.Jotform.models.jotform_form_model import JotformForm as JotformFormEntity, JotformCredential as JotformCredentialEntity
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort

from app.domain.Jotform.models.jotform_form_model import JotformFormAssignment as JotformFormAssignmentEntity

from app.adapters.sql_model_adapter.jotform.models.jotform import JotformCredential as JotformCredentialSQL, \
    JotformForm as JotformFormSQL, jotform_assignment_to_domain
from app.adapters.sql_model_adapter.jotform.models.jotform import jotform_credential_apply_sql,jotform_credential_to_domain, jotform_form_apply_sql, jotform_form_to_domain
from app.adapters.sql_model_adapter.jotform.models.jotform import JotformFormAssignment as JotformFormAssignmentSQL

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
            form_id=form.form_id,
            name=form.name,
            url = form.url,
            status = form.status,
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

        return jotform_form_to_domain(result) if result else None

    def get_forms_by_business_id(self, business_id: int) -> List[JotformFormEntity]:
        result = self.db.exec(
            select(JotformFormSQL)
            .join(JotformCredentialSQL, JotformCredentialSQL.id == JotformFormSQL.credential_id)
            .where(JotformCredentialSQL.business_id == business_id)
        ).all()

        return [jotform_form_to_domain(item) for item in result]

    def get_form_by_credential_id(self, credential_id: int) -> List[JotformFormEntity]:
        result = self.db.exec(
            select(JotformFormSQL)
            .where(JotformFormSQL.credential_id == credential_id)
        ).all()
        return [jotform_form_to_domain(item) for item in result]

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

    def create_assignment(self, assignment: JotformFormAssignmentEntity) -> JotformFormAssignmentEntity:
        form_assignment = JotformFormAssignmentSQL(
            category_id=assignment.category_id,
            form_id=assignment.form_id,
            business_member_id= assignment.business_member_id,
        )
        self.db.add(form_assignment)
        self.db.commit()
        self.db.refresh(form_assignment)
        return jotform_assignment_to_domain(form_assignment)

    def get_assignment_by_member_and_category(self, business_member_id: int, category_id: int) -> Optional[JotformFormAssignmentEntity]:
        result = self.db.exec(
            select(JotformFormAssignmentSQL)
            .where(JotformFormAssignmentSQL.category_id == category_id)
            .where(JotformFormAssignmentSQL.business_member_id == business_member_id)
            .where(JotformFormSQL.is_active == True)
        ).first()
        return jotform_assignment_to_domain(result) if result else None

    def get_assignments_for_form(self, form_id: int) -> List[JotformFormAssignmentEntity]:
        result = self.db.exec(
            select(JotformFormAssignmentSQL)
            .where(JotformFormAssignmentSQL.form_id == form_id)
        ).all()
        return [jotform_assignment_to_domain(item) for item in result] if result else None

    def delete_assignment(self, assignment_id: int) -> bool:
        assignment = self.db.get(JotformFormAssignmentSQL, assignment_id)
        if not assignment:
            return False
        self.db.delete(assignment)
        self.db.commit()
        return True

    def get_form_by_category_and_member(self, category_id: int, member_id: int) -> Optional[JotformFormEntity]:
        result = self.db.exec(
            select(JotformFormSQL)
            .join(JotformFormAssignmentSQL, JotformFormAssignmentSQL.form_id == JotformFormSQL.id)
            .where(JotformFormAssignmentSQL.category_id == category_id)
            .where(JotformFormAssignmentSQL.business_member_id == member_id)
            .where(JotformFormSQL.is_active == True)
        ).first()
        return jotform_form_to_domain(result) if result else None