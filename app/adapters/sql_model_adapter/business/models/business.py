from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from app.domain.business.models.business_model import Business as BusinessEntity

class Business(SQLModel, table=True):
    __tablename__ = "businesses"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    description: Optional[str] = None

    owner_id: int = Field(foreign_key="user.id")

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


def _to_domain(obj: Business) -> BusinessEntity:
    return BusinessEntity(
        id=obj.id,
        name=obj.name,
        description=obj.description,
        owner_id=obj.owner_id,
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )

def _apply_to_sql(entity: BusinessEntity, sql: Business) -> None:
    sql.name = entity.name
    sql.description = entity.description

