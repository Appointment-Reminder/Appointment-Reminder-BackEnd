from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.db.models.user import User


class UserGuard:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def ensure_user_exists(self, user_id: int) -> User:
        pass

    def ensure_user_email_exists(self, user_email: str) -> User:
        user = self.user_repo.get_by_email(user_email)
        if user:
            raise HTTPException(status_code=404, detail="User doesnt exist")

        return user