
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

from app.domain.user.models.user import User as UserEntity

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    hashed_password: str

    # User's own memberships
    business_members: list["BusinessMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "[BusinessMember.user_id]"
        }
    )

    # Members this user invited
    invited_members: list["BusinessMember"] = Relationship(
        back_populates="invited_by_user",
        sa_relationship_kwargs={
            "foreign_keys": "[BusinessMember.invited_by]"
        }
    )

def _to_domain(sql: User):
    return UserEntity(
        id=sql.id,
        email=sql.email,
        name=sql.name,
        hashed_password=sql.hashed_password,
        business_members = [],
        invited_members = []
    )

