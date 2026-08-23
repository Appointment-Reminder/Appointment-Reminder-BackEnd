from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BusinessCreate(BaseModel):
    """Schema for creating business"""
    name: str
    description: Optional[str] = None

class BusinessRead(BaseModel):
    """Schema for reading business"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BusinessWithRole(BaseModel):
    """Schema for reading a business with user's role"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    my_role: str

    class Config:
        from_attributes = True
class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
