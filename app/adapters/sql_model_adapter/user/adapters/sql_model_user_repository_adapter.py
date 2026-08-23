from sqlalchemy.orm import Session
from sqlmodel import select

from app.domain.user.models.user import User as UserEntity
from app.adapters.sql_model_adapter.user.models.user import User as UserSQL, _to_domain
from app.domain.user.port.user_repository_port import UserRepositoryPort


class SQLModelUserRepositoryAdapter(UserRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: UserEntity) -> UserEntity:
        sql_obj = UserSQL(
            email=user.email,
            name=user.name,
            hashed_password=user.hashed_password,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return _to_domain(sql_obj)

    def get_by_id(self, user_id: int) -> UserEntity:
        result = self.db.get(UserSQL, user_id)
        return _to_domain(result) if result else None

    def get_by_email(self, email: str) -> UserEntity:
        result = self.db.exec(
            select(UserSQL).where(UserSQL.email == email)
        ).first()
        return _to_domain(result) if result else None

    def get_all(self) -> list[UserEntity]:
        result = self.db.exec(select(UserSQL)).all()
        return [_to_domain(user) for user in result] if result else []

    def delete(self, user_id: int) -> bool:
        found_user = self.db.get(UserSQL, user_id)
        if not found_user:
            return False

        self.db.delete(found_user)
        self.db.commit()
        return True