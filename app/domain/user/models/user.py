from dataclasses import dataclass
from typing import Optional, List



@dataclass
class User:
    email: str
    name: str
    hashed_password: str
    id: Optional[int] = None
    business_members : List[object] = None
    invited_members: List[object] = None