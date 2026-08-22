import secrets
from datetime import datetime
from typing import Optional, List

from sqlalchemy import UniqueConstraint, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

from app.domain.Jotform.models.jotform_form_model import JotformCredential as JotformCredentialEntity, JotformForm as JotformFormEntity
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
    credential_id: int = Field(foreign_key="jotform_credentials.id")
    category_id: int = Field(foreign_key="package_category.id")

    form_id: str
    name: str

    member_assigns: List[int] = Field(sa_column=Column(JSONB))  # business_member ids
    field_mapping: List[dict] = Field(sa_column=Column(JSONB))  # [{target_key, qid, subkey}]

    webhook_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32), unique=True, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


def jotform_form_to_domain(sql: JotformForm) -> JotformFormEntity:
    return JotformFormEntity(
        id=sql.id,
        credential_id=sql.credential_id,
        category_id=sql.category_id,
        form_id=sql.form_id,
        name=sql.name,
        member_assigns=sql.member_assigns,
        field_mapping=sql.field_mapping,
        webhook_token=sql.webhook_token,
        is_active=sql.is_active,
        created_at=sql.created_at,
    )

def jotform_form_apply_sql(sql: JotformForm, obj: JotformFormEntity) -> None:
    sql.name = obj.name
    sql.member_assigns = obj.member_assigns
    sql.field_mapping = obj.field_mapping