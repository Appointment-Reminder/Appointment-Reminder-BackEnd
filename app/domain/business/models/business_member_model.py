from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    PHOTOGRAPHER = "photographer"
    ASSISTANT = "assistant"

@dataclass()
class BusinessMember:
    id: int
    business_id: int
    user_id: int
    role: MemberRole
    invited_at: datetime
    invited_by: int
    joined_at: datetime
    is_active: bool
    created_at: datetime

