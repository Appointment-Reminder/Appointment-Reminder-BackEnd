from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.db.models.business_member import MemberRole


class InvitationCreate(BaseModel):
    invitee_email: EmailStr
    role: MemberRole = MemberRole.PHOTOGRAPHER


class InvitationRead(BaseModel):
    id: int
    business_id: int
    invited_by: int
    invitee_email: str
    role: str
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class InvitationAcceptDecline(BaseModel):
    token: str