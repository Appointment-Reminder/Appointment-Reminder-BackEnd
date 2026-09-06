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
    credential_id: int
    category_id: int
    form_id: str
    name: str
    member_assigns: List[int]
    field_mapping: List[dict]
    webhook_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    id: Optional[int] = None

@dataclass
class JotformQuestion:
    id: int
    name: str


