from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class BusinessMemberRead(BaseModel):
    """Schema for reading a business member"""
    id: int
    business_id: int
    user_id: int
    role: str
    webhook_token: str
    invited_by: Optional[int]
    invited_at: datetime
    joined_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BusinessMemberInvite(BaseModel):
    email: EmailStr
    role: str = "Photographer"

