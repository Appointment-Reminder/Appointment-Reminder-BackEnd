from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"

@dataclass(frozen=True)
class BusinessMemberInvitation:
    id: int
    business_id: int
    invited_by: int

    invitee_email: str
    invitee_user_id: Optional[int]

    role: str
    token: str
    status: str

    created_at: datetime
    expires_at: datetime
    responded_at: datetime