from typing import Optional

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
    jotform_alias: Optional[str]


class PackageUpdate(BaseModel):
    id: int
    name: str
    description: str
    jotform_alias: Optional[str] = None



