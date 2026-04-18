from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Business(SQLModel, table=True):
    __tablename__ = "business"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    description: Optional[str] = None

    Owner_id: int = Field(foreign_key="user.id")

    webhook_token: str = Field(unique = True, index=True)

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
