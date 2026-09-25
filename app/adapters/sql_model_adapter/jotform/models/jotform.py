import secrets
from datetime import datetime
from typing import Optional, List

from sqlalchemy import UniqueConstraint, Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

from app.domain.Jotform.models.jotform_form_model import JotformCredential as JotformCredentialEntity, \
    JotformForm as JotformFormEntity, JotformFormAssignment as JotformFormAssignmentEntity, JotformQuestion


class JotformCredential(SQLModel, table=True):
    __tablename__ = "jotform_credentials"
    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    label: str
    api_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)



def jotform_credential_to_domain(sql: JotformCredential) -> JotformCredentialEntity:
    return JotformCredentialEntity(
        id=sql.id,
        business_id=sql.business_id,
        label=sql.label,
        api_key=sql.api_key,
        created_at=sql.created_at,
    )

def jotform_credential_apply_sql(sql: JotformCredential, obj: JotformCredentialEntity) -> None:
    sql.label = obj.label
    sql.api_key = obj.api_key

class JotformForm(SQLModel, table=True):
    __tablename__ = "jotform_forms"
    __table_args__ = (
        UniqueConstraint("credential_id", "form_id", name="uq_jotform_form"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    credential_id: int = Field(sa_column=Column(ForeignKey("jotform_credentials.id", ondelete="CASCADE")))

    form_id: str
    name: str
    status: str = Field(default="active")
    url: Optional[str] = Field(default=None)


    field_mapping: List[dict] = Field(sa_column=Column(JSONB))  # [{target_key, qid, subkey}]

    webhook_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32), unique=True, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    questions: List[dict] = Field(default_factory=list, sa_column=Column(JSONB))


def jotform_form_to_domain(sql: JotformForm) -> JotformFormEntity:
    return JotformFormEntity(
        id=sql.id,
        credential_id=sql.credential_id,
        form_id=sql.form_id,
        name=sql.name,
        status=sql.status,
        url=sql.url,
        field_mapping=sql.field_mapping,
        webhook_token=sql.webhook_token,
        is_active=sql.is_active,
        created_at=sql.created_at,
        questions=[JotformQuestion(id=q["id"], name=q["name"], subkeys=q.get("subkeys", [])) for q in sql.questions] if sql.questions else [],
    )

def jotform_form_apply_sql(sql: JotformForm, obj: JotformFormEntity) -> None:
    sql.name = obj.name
    sql.field_mapping = obj.field_mapping
    sql.questions = [{"id": q.id, "name": q.name, "subkeys": q.subkeys} for q in obj.questions]

class JotformFormAssignment(SQLModel, table= True):
    __tablename__ = "jotform_form_assignments"
    __table_args__  = (
        UniqueConstraint("business_member_id", "category_id", name="uq_jotform_form_assignment"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    form_id: int = Field(sa_column=Column(ForeignKey("jotform_forms.id", ondelete="CASCADE")))
    business_member_id: int = Field(foreign_key="business_members.id")
    category_id: int = Field(foreign_key="package_category.id")

def jotform_assignment_to_domain(sql: JotformFormAssignment) -> JotformFormAssignmentEntity:
    return JotformFormAssignmentEntity(
        id=sql.id,
        business_member_id=sql.business_member_id,
        category_id=sql.category_id,
        form_id=sql.form_id,
    )

def assignment_apply_sql(sql: JotformFormAssignment, obj: JotformFormAssignmentEntity) -> None:
    sql.form_id = obj.form_id
    sql.business_member_id = obj.business_member_id
    sql.category_id = obj.category_id