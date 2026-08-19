import secrets
from datetime import datetime
from typing import Optional, List

from sqlalchemy import UniqueConstraint, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field


class JotformCredential(SQLModel, table=True):
    __tablename__ = "jotform_credentials"
    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id")
    label: str
    api_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JotformForm(SQLModel, table=True):
    __tablename__ = "jotform_forms"
    __table_args__ = (
        UniqueConstraint("credential_id", "form_id", name="uq_jotform_form"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    credential_id: int = Field(foreign_key="jotform_credentials.id")
    business_id: int = Field(foreign_key="businesses.id", index=True)
    category_id: int = Field(foreign_key="package_category.id")

    form_id: str
    name: str

    member_assigns: List[int] = Field(sa_column=Column(JSONB))  # business_member ids
    field_mapping: List[dict] = Field(sa_column=Column(JSONB))  # [{target_key, qid, subkey}]

    webhook_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32), unique=True, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


