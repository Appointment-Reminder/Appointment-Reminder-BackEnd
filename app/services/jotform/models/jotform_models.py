from dataclasses import dataclass, Field
from datetime import datetime
from typing import Optional, List


@dataclass
class JotformForm:
    id: int
    form_id: int
    business_id: int
    name: str
    member_assigns: List[dict]
    webhook_token: str
    field_mapping: List[dict]
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.now)

@dataclass
class JotformQuestion:
    id: int
    name: str

@dataclass
class JotformCredential:
    id: Optional[int]
    business_id: int
    label: str
    api_key: str
    created_at: datetime = Field(default_factory=datetime.now)



