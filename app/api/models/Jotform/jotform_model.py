from datetime import datetime

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class JotformQuestionRead(BaseModel):
    id: str
    name: str
    options: list[str] = []

class JotformWebhookPayload(BaseModel):
    """Schema for incoming hotform webhook"""
    submissionID: str
    formId: str
    rawRequest: Dict[str, Any]

class JotformProcessingResult(BaseModel):
    """Result of processing Jotform submission"""
    success: bool
    appointment_id: int
    submission_id: str
    photographer_id: int

class JotformFormCreate(BaseModel):
    credential_id: int
    form_id: str
    name: str
    field_mapping: List[dict]

class JotformFormRead(BaseModel):
    """Read a jotform form"""
    id: int
    form_id: str
    name: str
    webhook_token: str
    field_mapping: Optional[List[dict]]
    questions: List[JotformQuestionRead] = []
    created_at: datetime

    class Config:
        from_attributes = True

class JotformFormUpdate(BaseModel):
    id: int
    name: str
    member_assigns: List[int]
    field_mapping: List[dict]

class JotformFormDelete(BaseModel):
    id: int
class JotformCredentialCreate(BaseModel):
    business_id: int
    label: str
    api_key: str

class JotformCredentialRead(BaseModel):
    id: int
    business_id: int
    label: str
    api_key: str
    created_at: datetime
    questions: List[dict]

class JotformCredentialUpdate(BaseModel):
    id:int
    label: str
    api_key: str

class JotformCredentialDelete(BaseModel):
    id: int

class JotformAssignmentCreate(BaseModel):
    form_id: int
    business_member_id: int
    category_id: int
class JotformAssignmentRead(BaseModel):
    id: int
    form_id: int
    business_member_id: int
    category_id: int




