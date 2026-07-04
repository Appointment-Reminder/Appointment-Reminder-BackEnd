from datetime import datetime

from pydantic import BaseModel


class BusinessMemberFormCreate(BaseModel):
    business_member_id: int
    category_id: int
    jotform_field_map: str

class BusinessMemberFormRead(BaseModel):
    id: int
    business_member_id: int
    category_id: int
    webhook_token: str
    jotform_field_map: str
    created_at: datetime
class BusinessMemberFormUpdate(BaseModel):
    id: int
    business_member_id: int
    category_id: int
    jotform_field_map: str