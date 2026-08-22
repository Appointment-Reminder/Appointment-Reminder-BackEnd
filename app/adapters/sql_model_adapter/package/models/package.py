from typing import Optional

from sqlmodel import SQLModel, Field


class Package(SQLModel, table= True):
    __tablename__ = "package"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: Optional[int] = Field(default=None, foreign_key='businesses.id')
    category_id: Optional[int] = Field(default=None, foreign_key='package_category.id')

    name: str
    description: str
    is_active: bool

    jotform_alias: Optional[str] = None



