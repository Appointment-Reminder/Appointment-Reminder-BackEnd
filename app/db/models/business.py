from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class Business(SQLModel, table=True):
    __tablename__ = "businesses"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    description: Optional[str] = None

    owner_id: int = Field(foreign_key="user.id")

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
