from datetime import datetime
from typing import Optional
from app.db.models.business_member import BusinessMember
from app.db.models.package.package_category import PackageCategory
from sqlmodel import SQLModel, Field


class BusinessMemberForm(SQLModel, table=True):
    __tablename__ = "business_member_form"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_member_id: int = Field(default=None, foreign_key='business_members.id')
    category_id: int = Field(default=None, foreign_key='package_category.id')
    webhook_token: str
    jotform_field_map: str
    is_active: bool
    created_at: datetime