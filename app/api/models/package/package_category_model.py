from sqlmodel import SQLModel


class PackageCategoryCreate(SQLModel):
    business_id: int
    name: str

class PackageCategoryRead(SQLModel):
    id: int
    name: str
    business_id: int

class PackageCategoryUpdate(SQLModel):
    id: int
    name: str
