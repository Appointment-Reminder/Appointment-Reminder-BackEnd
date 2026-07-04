from typing import Optional

from sqlmodel import SQLModel, Field
from app.db.models.business import Business

class PackageCategory(SQLModel, table= True):
    __tablename__ = "package_category"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: Optional[int] = Field(default=None, foreign_key="businesses.id")
    name: str