from sqlmodel import Session
from sqlmodel import select

from app.db.models.user import User


class UserRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.exec(
            select(User).where(User.email == email)
        ).first()

    def get_all(self) -> list[User]:
        return self.db.exec(select(User)).all()

    def delete(self, user_id: int) -> bool:
        found_user = self.db.get(User, user_id)
        if not found_user:
            return False

        self.db.delete(found_user)
        self.db.commit()
        return True