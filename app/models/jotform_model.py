from pydantic import BaseModel
from typing import Dict, Any

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