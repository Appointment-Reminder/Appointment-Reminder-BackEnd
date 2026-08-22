from app.domain.user.errors.user_errors import UserError
from app.domain.user.models.user import User
from app.domain.user.port.user_repository_port import UserRepositoryPort


class UserGuard:
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo

    def ensure_user_exists(self, user_id: int) -> User:
        pass

    def ensure_user_email_exists(self, user_email: str) -> User:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise UserError()
        return user