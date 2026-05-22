from pydantic import BaseModel

from app.models.userModel import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead