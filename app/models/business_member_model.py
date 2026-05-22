from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.db.models.business_member import MemberRole
from app.models.userModel import UserRead


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

    user: Optional[UserRead]
    invited_by_user: Optional[UserRead]

    class Config:
        from_attributes = True

class BusinessMemberInvite(BaseModel):
    email: EmailStr
    role: str = "Photographer"

class BusinessMemberUpdate(BaseModel):
    role:str
    is_active:bool

class BusinessMemberInvite(BaseModel):
    user_email: EmailStr
    role: str = MemberRole.PHOTOGRAPHER

