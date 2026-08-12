from datetime import datetime

from pydantic import BaseModel
from typing import Dict, Any, List


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
    form_id: str
    member_assigns: List[dict]
    field_mapping: List[dict]

class JotformFormRead(BaseModel):
    """Read a jotform form"""
    id: int
    business_id: int
    form_id: str
    name: str
    member_assigns: List[dict]
    webhook_token: str
    field_mapping: List[dict]
    created_at: datetime

class JotformFormUpdate(BaseModel):
    id: int
    name: str
    member_assigns: List[dict]
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

class JotformCredentialUpdate(BaseModel):
    id:int
    label: str
    api_key: str

class JotformCredentialDelete(BaseModel):
    id: int




