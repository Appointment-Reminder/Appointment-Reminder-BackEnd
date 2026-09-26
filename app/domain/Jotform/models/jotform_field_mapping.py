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
    ## APPOTINMENT INFO
    SubmissionFieldDef("appointment_date", "Appointment Date", FieldType.DATE, required=True),
    SubmissionFieldDef("appointment_location", "Appointment Location", FieldType.TEXT, required=True),
    SubmissionFieldDef("appointment_note","Appointment Note", FieldType.TEXT, required=False),
    SubmissionFieldDef("guest_count", "Number Of People", FieldType.NUMBER),

    ## CLIENT INFO
    SubmissionFieldDef("client_first_name", "Client First Name", FieldType.TEXT, required=True),
    SubmissionFieldDef("client_last_name", "Client Last Name", FieldType.TEXT, required=True),
    SubmissionFieldDef("client_source_location", "Where Client Is From", FieldType.TEXT),
    SubmissionFieldDef("client_email", "Client Email", FieldType.TEXT, required=False),
    SubmissionFieldDef("client_phone_country_code", "Client Phone country code", FieldType.TEXT, required=False),
    SubmissionFieldDef("client_phone", "Client Phone", FieldType.TEXT, required=False),
    SubmissionFieldDef("referral_source", "Where Did You Find Us", FieldType.TEXT),

    ## PACKAGE INFO
    SubmissionFieldDef("package", "Package Chosen", FieldType.TEXT, required=True),
    SubmissionFieldDef("privacy_opt_out", "Privacy Opt Out", FieldType.BOOL),
    SubmissionFieldDef("add_ons", "Add Ons", FieldType.LIST),
]

SUBMISSION_FIELD_KEYS: set[str] = {f.key for f in SUBMISSION_FIELDS}