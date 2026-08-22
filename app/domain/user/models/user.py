from dataclasses import dataclass
from typing import Optional

from models.business_member import BusinessMember


@dataclass
class User:
    id: Optional[int]
    email: str
    name: str
    hashed_password: str

    business_members: list[BusinessMember]
    invited_members: list[BusinessMember]