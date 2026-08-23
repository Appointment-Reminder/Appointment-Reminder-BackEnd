from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.package.models.package_category_model import PackageCategory as PackageCategoryEntity
class PackageCategory(SQLModel, table= True):
    __tablename__ = "package_category"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: Optional[int] = Field(default=None, foreign_key="businesses.id")
    name: str

def _to_domain(sql: PackageCategory) -> PackageCategoryEntity:
    return PackageCategoryEntity(
        id=sql.id,
        business_id=sql.business_id,
        name=sql.name,
    )

def _apply_sql(sql: PackageCategory, obj: PackageCategoryEntity) -> None:
    sql.name = obj.name
