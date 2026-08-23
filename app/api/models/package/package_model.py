from pydantic import BaseModel


class PackageCreate(BaseModel):
    name: str
    description: str
    business_id: int
    category_id: int

class PackageRead(BaseModel):
    id: int
    business_id: int
    category_id: int
    name: str
    description: str
    is_active: bool


class PackageUpdate(BaseModel):
    id: int
    business_id: int
    category_id: int
    name: str
    description: str



