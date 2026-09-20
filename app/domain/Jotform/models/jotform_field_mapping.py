from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class JotformFieldMapping:
    form_id: int
    target_key: str
    qid: str
    priority: int
    subkey: str = None
    id: Optional[int] = None


class FieldType(str, Enum):
    TEXT = "text"
    DATE = "date"
    BOOL = "bool"
    LIST = "list"
    NUMBER = "number"

@dataclass(frozen=True)
class SubmissionFieldDef:
    key: str
    label: str
    type: FieldType
    required: bool = False

SUBMISSION_FIELDS: list[SubmissionFieldDef] = [
    SubmissionFieldDef("appointment_date", "Appointment Date", FieldType.DATE, required=True),
    SubmissionFieldDef("package", "Package Chosen", FieldType.TEXT, required=True),
    SubmissionFieldDef("privacy_opt_out", "Privacy Opt Out", FieldType.BOOL),
    SubmissionFieldDef("client_name", "Client Name", FieldType.TEXT, required=True),
    SubmissionFieldDef("client_source_location", "Where Client Is From", FieldType.TEXT),
    SubmissionFieldDef("referral_source", "Where Did You Find Us", FieldType.TEXT),
    SubmissionFieldDef("add_ons", "Add Ons", FieldType.LIST),
    SubmissionFieldDef("guest_count", "Number Of People", FieldType.NUMBER),
    SubmissionFieldDef("client_email", "Client Email", FieldType.TEXT, required=True),
]

SUBMISSION_FIELD_KEYS: set[str] = {f.key for f in SUBMISSION_FIELDS}