# tests/domain/jotform/test_full_submission_resolution.py
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, FieldType, SubmissionFieldDef
from app.domain.Jotform.models.jotform_form_model import JotformForm
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.Jotform.service.jotform_webhook_parser import parse_jotform_raw_request


@pytest.fixture
def raw_request():
    path = Path(__file__).parents[3] / "tests" / "webhook.json"
    return json.loads(path.read_text(encoding="utf-8"))

@pytest.fixture
def parsed(raw_request):
    return parse_jotform_raw_request(raw_request)

@pytest.fixture
def jotform_repo():
    return Mock()

@pytest.fixture
def service(jotform_repo):
    return JotformService(business_guard=Mock(), jotform_guard=Mock(), package_repo=Mock(),
                           member_repo=Mock(), jotform_repo=jotform_repo, jotform_api=Mock())

@pytest.fixture
def form():
    return JotformForm(id=10, form_id="261174297742362", name="Booking", credential_id=5)


class TestFullResolutionAgainstRealPayload:
    def test_client_name_via_subkey(self, service, jotform_repo, form, parsed):
        fields = [SubmissionFieldDef("client_name", "x", FieldType.TEXT, required=True)]
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
            jotform_repo.get_field_mappings.return_value = [
                JotformFieldMapping(form_id=10, target_key="client_name", qid="3", subkey="first", priority=0)
            ]
            result = service.resolve_submission(form=form, raw_answers=parsed)
            assert result["client_name"] == "John"

    def test_package_resolves_byte_identical_including_nbsp(self, service, jotform_repo, form, parsed):
        fields = [SubmissionFieldDef("package", "x", FieldType.TEXT, required=True)]
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
            jotform_repo.get_field_mappings.return_value = [
                JotformFieldMapping(form_id=10, target_key="package", qid="123", priority=0)
            ]
            result = service.resolve_submission(form=form, raw_answers=parsed)
            assert result["package"] == "PARISIAN DREAM\u00a012 HOURS (600 Edited) - \u20ac2000"
            assert "\u00a0" in result["package"]

    def test_appointment_date_via_subkey_ignores_duration_and_timezone(self, service, jotform_repo, form, parsed):
        fields = [SubmissionFieldDef("appointment_date", "x", FieldType.DATE, required=True)]
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
            jotform_repo.get_field_mappings.return_value = [
                JotformFieldMapping(form_id=10, target_key="appointment_date", qid="65", subkey="date", priority=0)
            ]
            result = service.resolve_submission(form=form, raw_answers=parsed)
            assert result["appointment_date"] == "2026-07-31 11:00"

    def test_unmapped_field_resolves_none_no_crash(self, service, jotform_repo, form, parsed):
        fields = [SubmissionFieldDef("guest_count", "x", FieldType.NUMBER, required=False)]
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
            jotform_repo.get_field_mappings.return_value = []
            result = service.resolve_submission(form=form, raw_answers=parsed)
            assert result["guest_count"] is None