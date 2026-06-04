from typing import Optional

from sqlmodel import SQLModel, Field


class JotformPackageAlias(SQLModel, table=True):
    __tablename__ = "jotform_package_alias"

    id: Optional[int] = Field(default=None, primary_key=True)
    package_id: int = Field(default=None, foreign_key='Package.id')
    alias: str
