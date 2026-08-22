from dataclasses import dataclass

from app.domain.user.models.user import User


@dataclass
class Token:
    access_token: str
    token_type: str
    user: User