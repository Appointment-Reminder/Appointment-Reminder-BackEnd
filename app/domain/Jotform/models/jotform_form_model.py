from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class JotformCredential:
    business_id: int
    label: str
    api_key: str
    id: Optional[int] = None
    created_at: datetime = datetime.now()


@dataclass
class JotformForm:
    id: Optional[int]
    credential_id: int
    category_id: int
    form_id: str
    name: str
    member_assigns: List[int]
    field_mapping: List[dict]
    webhook_token: str
    is_active: bool
    created_at: datetime


