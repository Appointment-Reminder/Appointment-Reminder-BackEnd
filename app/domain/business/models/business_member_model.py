from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from app.domain.user.models.user import User


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    PHOTOGRAPHER = "photographer"
    ASSISTANT = "assistant"

@dataclass()
class BusinessMember:
    business_id: int
    user_id: int
    role: MemberRole
    id: Optional[int] = None
    invited_at: Optional[datetime] = None
    invited_by: Optional[int] = None
    joined_at: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    user: Optional[User] = None
    invited_by_user: Optional[User] = None

