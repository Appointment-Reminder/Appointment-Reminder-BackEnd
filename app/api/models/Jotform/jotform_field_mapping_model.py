from typing import Optional

from pydantic import BaseModel


class JotformFieldMappingItem(BaseModel):
    target_key: str
    qid: str
    priority: int
    subkey: Optional[str] = None

class JotformFieldMappingRead(BaseModel):
    id: int
    form_id: int
    target_key: str
    qid: str
    priority: int
    subkey: Optional[str] = None

    class Config:
        from_attributes = True

class JotformFieldMappingUpdate(BaseModel):
    mapping: list[JotformFieldMappingItem]

class SubmissionFieldRead(BaseModel):
    key: str
    label: str
    type: str
    required: bool

    class Config:
        from_attributes = True