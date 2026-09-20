# tests/domain/jotform/test_resolve_submission.py
import pytest
from unittest.mock import Mock, patch

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, SubmissionFieldDef, FieldType
from app.domain.Jotform.models.jotform_form_model import JotformForm
from app.domain.Jotform.service.jotform_service import JotformService


@pytest.fixture
def jotform_repo():
    return Mock()

@pytest.fixture
def service(jotform_repo):
    return JotformService(
        business_guard=Mock(), jotform_guard=Mock(), package_repo=Mock(),
        member_repo=Mock(), jotform_repo=jotform_repo, jotform_api=Mock(),
    )

@pytest.fixture
def form():
    return JotformForm(id=10, form_id="ext-1", name="Booking Form", credential_id=5)

def _mapping(target_key, qid, priority=0, subkey=None):
    return JotformFieldMapping(form_id=10, target_key=target_key, qid=qid, priority=priority, subkey=subkey)

def single_field(key="client_name", required=False):
    return [SubmissionFieldDef(key, key, FieldType.TEXT, required=required)]


class TestResolveSubmission:
    def test_resolves_all_fields_when_present(self, service, jotform_repo, form):
        fields = [
            SubmissionFieldDef("appointment_date", "x", FieldType.DATE, required=True),
            SubmissionFieldDef("package", "x", FieldType.TEXT, required=True),
            SubmissionFieldDef("client_name", "x", FieldType.TEXT, required=True),
        ]
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
            jotform_repo.get_field_mappings.return_value = [
                _mapping("appointment_date", "1"), _mapping("package", "2"), _mapping("client_name", "3"),
            ]
            raw = {"1": {"answer": "2026-10-01"}, "2": {"answer": "Gold"}, "3": {"answer": "Jane"}}
            result = service.resolve_submission(form=form, raw_answers=raw)
            assert result == {"appointment_date": "2026-10-01", "package": "Gold", "client_name": "Jane"}

    def test_uses_first_non_null_by_priority(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field()):
            jotform_repo.get_field_mappings.return_value = [
                _mapping("client_name", "1", priority=0), _mapping("client_name", "2", priority=1),
            ]
            raw = {"1": {"answer": ""}, "2": {"answer": "Jane Doe"}}
            assert service.resolve_submission(form=form, raw_answers=raw)["client_name"] == "Jane Doe"

    def test_stops_at_first_non_null(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field()):
            jotform_repo.get_field_mappings.return_value = [
                _mapping("client_name", "1", priority=0), _mapping("client_name", "2", priority=1),
            ]
            raw = {"1": {"answer": "First"}, "2": {"answer": "Second"}}
            assert service.resolve_submission(form=form, raw_answers=raw)["client_name"] == "First"

    def test_sorts_by_priority_regardless_of_repo_order(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field()):
            jotform_repo.get_field_mappings.return_value = [
                _mapping("client_name", "2", priority=1), _mapping("client_name", "1", priority=0),
            ]
            raw = {"1": {"answer": "Correct"}, "2": {"answer": "Wrong"}}
            assert service.resolve_submission(form=form, raw_answers=raw)["client_name"] == "Correct"

    def test_reads_subkey_from_composite_answer(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field()):
            jotform_repo.get_field_mappings.return_value = [_mapping("client_name", "1", subkey="first")]
            raw = {"1": {"answer": {"first": "John", "last": "Smith"}}}
            assert service.resolve_submission(form=form, raw_answers=raw)["client_name"] == "John"

    def test_missing_qid_resolves_none(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field()):
            jotform_repo.get_field_mappings.return_value = [_mapping("client_name", "99")]
            assert service.resolve_submission(form=form, raw_answers={})["client_name"] is None

    def test_empty_string_and_list_treated_as_null(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field(key="add_ons")):
            jotform_repo.get_field_mappings.return_value = [
                _mapping("add_ons", "1", priority=0), _mapping("add_ons", "2", priority=1),
            ]
            raw = {"1": {"answer": []}, "2": {"answer": ["Extra Album"]}}
            assert service.resolve_submission(form=form, raw_answers=raw)["add_ons"] == ["Extra Album"]

    def test_required_field_unmapped_raises(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field(required=True)):
            jotform_repo.get_field_mappings.return_value = []
            with pytest.raises(JotformDomainError):
                service.resolve_submission(form=form, raw_answers={})

    def test_required_field_mapped_but_empty_raises(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field(required=True)):
            jotform_repo.get_field_mappings.return_value = [_mapping("client_name", "1")]
            raw = {"1": {"answer": ""}}
            with pytest.raises(JotformDomainError):
                service.resolve_submission(form=form, raw_answers=raw)

    def test_optional_field_unmapped_resolves_none_no_raise(self, service, jotform_repo, form):
        with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", single_field(required=False)):
            jotform_repo.get_field_mappings.return_value = []
            result = service.resolve_submission(form=form, raw_answers={})
            assert result["client_name"] is None