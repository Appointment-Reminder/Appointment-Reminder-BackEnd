from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey
from sqlmodel import SQLModel, Field

from app.domain.addon.models.unresolved_addon import UnresolvedAddon as UnresolvedAddonEntity


class UnresolvedAddon(SQLModel, table=True):
    __tablename__ = "unresolved_addon"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(sa_column=Column(ForeignKey("appointments.id", ondelete="CASCADE"), index=True))
    raw_label: str
    resolved_addon_id: Optional[int] = Field(default=None, foreign_key="addon.id")
    resolved_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)


def _to_domain(sql: UnresolvedAddon) -> UnresolvedAddonEntity:
    return UnresolvedAddonEntity(
        id=sql.id,
        appointment_id=sql.appointment_id,
        raw_label=sql.raw_label,
        resolved_addon_id=sql.resolved_addon_id,
        resolved_at=sql.resolved_at,
    )
