from typing import Optional

from pydantic import BaseModel


class PackageCreate(BaseModel):
    name: str
    description: str
    business_id: int
    category_id: int
    package_duration: Optional[int] = None

class PackageRead(BaseModel):
    id: int
    business_id: int
    category_id: int
    name: str
    description: str
    is_active: bool
    package_duration: Optional[int] = None
    jotform_alias: Optional[str]


class PackageUpdate(BaseModel):
    id: int
    name: str
    description: str
    package_duration: Optional[int] = None
    jotform_alias: Optional[str] = None



