from datetime import datetime
from typing import Optional, List

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
    id: Optional[int] = Field(default=None, primary_key=True)
    form_id: int
    business_id: int = Field(foreign_key="businesses.id")
    name: str
    member_assigns: List[dict]
    webhook_token: str
    field_mapping: List[dict]
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)