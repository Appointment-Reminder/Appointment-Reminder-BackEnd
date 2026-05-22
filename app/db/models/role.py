from typing import Optional

from sqlmodel import SQLModel, create_engine, Field


class Role(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

