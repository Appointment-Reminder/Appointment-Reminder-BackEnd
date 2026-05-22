import secrets
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"

class BusinessInvitation(SQLModel, table=True):
    __tablename__ = "business_invitation"

    id: Optional[int] = Field(default=None, primary_key=True)

    business_id: int = Field(foreign_key="businesses.id", index=True)
    invited_by: int = Field(foreign_key="users.id")

    #Invitee email always required user_id filled in if they already exist
    invitee_email: str = Field(index=True)
    invitee_user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    role: str = Field(default="photographer")

    token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        unique=True,
        index=True
    )

    status: str = Field(default=InvitationStatus.PENDING)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime # set explicitly on creation eg now + 7 days

    responded_at: Optional[datetime] = None
