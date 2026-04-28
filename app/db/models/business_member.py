from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field
from sqlmodel import SQLModel
import secrets


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    PHOTOGRAPHER = "photographer"
    ASSISTANT = "assistant"

class BusinessMember(SQLModel, table=True):
    __tablename__ = "business_members"

    id: Optional[int] = Field(default=None, primary_key=True)

    business_id: int = Field(foreign_key="businesses.id")
    user_id: int = Field(foreign_key="user.id")

    role: str = Field(default = MemberRole.PHOTOGRAPHER)

    #each photographer gets their own webhook token
    webhook_token : str = Field(
        default_factory= lambda: secrets.token_urlsafe(32),
        unique=True,
        index=True
    )
    #Invitation system
    invited_by: Optional[int] = Field(foreign_key="user.id")
    invited_at: datetime = Field(default_factory= datetime.utcnow)
    joined_at: Optional[datetime] = None

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)


