from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.package.models.package import Package as PackageEntity

class Package(SQLModel, table= True):
    __tablename__ = "package"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: Optional[int] = Field(default=None, foreign_key='businesses.id')
    category_id: Optional[int] = Field(default=None, foreign_key='package_category.id')

    name: str
    description: str
    is_active: bool

    jotform_alias: Optional[str] = None


def _to_domain(sql: Package) -> PackageEntity:
    return PackageEntity(
        id=sql.id,
        business_id=sql.business_id,
        category_id=sql.category_id,
        name=sql.name,
        description=sql.description,
        is_active=sql.is_active,
        jotform_alias=sql.jotform_alias,
    )

def _apply_sql(sql: Package, obj: PackageEntity) -> None:
    sql.business_id = obj.business_id
    sql.category_id = obj.category_id
    sql.name = obj.name
    sql.description = obj.description



