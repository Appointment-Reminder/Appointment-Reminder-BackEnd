from dataclasses import dataclass
from typing import Optional

from app.domain.business.models.business_member_model import BusinessMember


@dataclass
class User:
    id: Optional[int]
    email: str
    name: str
    hashed_password: str

    business_members: list[BusinessMember]
    invited_members: list[BusinessMember]