from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.user.adapters.sql_model_user_repository_adapter import SQLModelUserRepositoryAdapter
from app.domain.user.guard.user_guard import UserGuard
from app.domain.user.models.user import User
from app.domain.user.port.user_repository_port import UserRepositoryPort

from fastapi import Request, HTTPException

from app.domain.user.service.user_service import decode_token


class UserProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_repo(self, db: Session) -> UserRepositoryPort:
        return SQLModelUserRepositoryAdapter(db=db)

    @provide
    def get_user_guard(self, repo: UserRepositoryPort) -> UserGuard:
        return UserGuard(repo)

    @provide(scope=Scope.REQUEST)
    def get_current_user(self, request: Request, repo: UserRepositoryPort) -> User:
        token = request.headers["authorization"].removeprefix("Bearer ")
        _, user_id = decode_token(token)
        user = repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user