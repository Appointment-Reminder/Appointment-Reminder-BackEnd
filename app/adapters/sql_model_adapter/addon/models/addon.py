from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.addon.models.addon import Addon as AddonEntity


class Addon(SQLModel, table=True):
    __tablename__ = "addon"

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="businesses.id", index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="package_category.id")

    name: str
    jotform_alias: str
    is_active: bool = Field(default=True)

    has_duration: bool = Field(default=False)
    has_quantity: bool = Field(default=False)
    duration_minutes: Optional[int] = Field(default=None)


def _to_domain(sql: Addon) -> AddonEntity:
    return AddonEntity(
        id=sql.id,
        business_id=sql.business_id,
        category_id=sql.category_id,
        name=sql.name,
        jotform_alias=sql.jotform_alias,
        is_active=sql.is_active,
        has_duration=sql.has_duration,
        has_quantity=sql.has_quantity,
        duration_minutes=sql.duration_minutes,
    )


def _apply_sql(sql: Addon, obj: AddonEntity) -> None:
    sql.category_id = obj.category_id
    sql.name = obj.name
    sql.jotform_alias = obj.jotform_alias
    sql.is_active = obj.is_active
    sql.has_duration = obj.has_duration
    sql.has_quantity = obj.has_quantity
    sql.duration_minutes = obj.duration_minutes
