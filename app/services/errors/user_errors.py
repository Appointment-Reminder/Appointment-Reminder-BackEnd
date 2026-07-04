from app.services.errors.error_base import ServiceError


class UserNotFound(ServiceError):
    def __init__(self, user_email: str):
        super().__init__(
            f"User {user_email} not found"
        )
        self.user_id = user_email

