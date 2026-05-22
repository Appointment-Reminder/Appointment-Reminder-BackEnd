
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class User(SQLModel, table=True):

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

