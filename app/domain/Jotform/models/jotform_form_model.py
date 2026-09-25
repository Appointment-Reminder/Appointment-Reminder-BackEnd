from dataclasses import dataclass, field
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
class JotformQuestion:
    id: int
    name: str
    options: list[str] = field(default_factory=list)
    subkeys: list[str] = field(default_factory=list)

@dataclass
class JotformForm:
    form_id: str
    name: str
    status: str = None
    url: str = None
    credential_id: int = None
    field_mapping: List[dict] = None
    webhook_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    questions: List[JotformQuestion] = field(default_factory=list)
    id: Optional[int] = None

@dataclass
class JotformFormAssignment:
    form_id: int
    business_member_id: int
    category_id: int
    id: Optional[int] = None



