# tests/test_jotform_service.py
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime

from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, SUBMISSION_FIELDS, SubmissionFieldDef, \
    FieldType
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_form_model import JotformCredential, JotformForm
from app.domain.business.errors.business_errors import BusinessError
from app.domain.user.models.user import User


@pytest.fixture
def user():
    return User(id=1, email="a@a.com", name="A", hashed_password="x")


@pytest.fixture
def service():
    return JotformService(
        business_guard=MagicMock(),
        jotform_guard=MagicMock(),
        package_repo=MagicMock(),
        member_repo=MagicMock(),
        jotform_repo=MagicMock(),
        jotform_api=MagicMock(),
    )

@pytest.fixture
def business_guard():
    return Mock()

@pytest.fixture
def jotform_guard():
    return Mock()

@pytest.fixture
def jotform_repo():
    return Mock()

@pytest.fixture
def package_repo():
    return Mock()

@pytest.fixture
def member_repo():
    return Mock()

@pytest.fixture
def jotform_api():
    return Mock()

@pytest.fixture
def service(business_guard, jotform_guard, package_repo, member_repo, jotform_repo, jotform_api):
    return JotformService(
        business_guard=business_guard,
        jotform_guard=jotform_guard,
        package_repo=package_repo,
        member_repo=member_repo,
        jotform_repo=jotform_repo,
        jotform_api=jotform_api,
    )

@pytest.fixture
def current_user():
    return User(id=1, email="owner@test.com", name="Owner", hashed_password="x")

@pytest.fixture
def form():
    return JotformForm(id=10, form_id="ext-1", name="Booking Form", credential_id=5)

@pytest.fixture
def credential():
    return JotformCredential(id=5, business_id=100, label="main", api_key="key")

@pytest.fixture
def minimal_fields():
    """Patch SUBMISSION_FIELDS as imported into jotform_service, not one required field to avoid noise in unrelated tests."""
    fields = [
        SubmissionFieldDef("client_name", "Client Name", FieldType.TEXT, required=False),
    ]
    with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
        yield fields

@pytest.fixture
def minimal_fields_client_source():
    """Patch SUBMISSION_FIELDS as imported into jotform_service, not one required field to avoid noise in unrelated tests."""
    fields = [
        SubmissionFieldDef("client_source_location", "Where Client Is From", FieldType.TEXT),
    ]
    with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
        yield fields

@pytest.fixture
def minimal_fields_adds_on_list():
    """Patch SUBMISSION_FIELDS as imported into jotform_service, not one required field to avoid noise in unrelated tests."""
    fields = [
        SubmissionFieldDef("add_ons", "Add Ons", FieldType.LIST),
    ]
    with patch("app.domain.Jotform.service.jotform_service.SUBMISSION_FIELDS", fields):
        yield fields

def test_create_credential_requires_admin(service, user):
    service.business_guard.ensure_admin_or_owner.side_effect = BusinessError()
    data = JotformCredential(business_id=1, label="l", api_key="k")

    with pytest.raises(BusinessError):
        service.create_jotform_credential(data, user)

    service.jotform_repo.create_credential.assert_not_called()


def test_create_credential_success(service, user):
    data = JotformCredential(business_id=1, label="l", api_key="k")
    service.jotform_repo.create_credential.return_value = data

    result = service.create_jotform_credential(data, user)

    service.business_guard.ensure_exists.assert_called_once_with(1)
    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == data


def test_delete_credential_checks_ownership_via_guard(service, user):
    cred = JotformCredential(id=5, business_id=1, label="l", api_key="k")
    service.jotform_guard.ensure_credential_exists.return_value = cred

    service.delete_jotform_credentials(5, user)

    service.business_guard.ensure_exists.assert_called_once_with(1)
    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    service.jotform_repo.delete_credential.assert_called_once_with(5)


def test_form_create_rejects_unknown_credential(service, user):
    service.jotform_guard.ensure_credential_exists.side_effect = JotformDomainError()
    data = JotformForm(credential_id=99, form_id="f1",
                        name="n")

    with pytest.raises(JotformDomainError):
        service.jotform_form_create(data, user)


def test_form_create_success(service, user):
    cred = JotformCredential(id=1, business_id=1, label="l", api_key="k")
    service.jotform_guard.ensure_credential_exists.return_value = cred
    data = JotformForm(credential_id=1, form_id="f1",
                        name="n")
    service.jotform_repo.create_form.return_value = data

    result = service.jotform_form_create(data, user)

    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == data


def test_get_form_by_id_checks_business_membership(service, user):
    form = JotformForm(id=10, credential_id=1, form_id="f1",
                        name="n")
    cred = JotformCredential(id=1, business_id=1, label="l", api_key="k")
    service.jotform_guard.ensure_form_exists.return_value = form
    service.jotform_guard.ensure_credential_exists.return_value = cred

    result = service.get_jotform_form_by_id("10", user)

    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == form


def test_delete_form_currently_broken(service, user):
    """
    Documents the bug: JotformForm has no `business_id` attribute,
    so this raises AttributeError instead of doing the delete.
    Fix delete_jotform_form to resolve business via credential_id first.
    """
    form = JotformForm(id=10, credential_id=1, form_id="f1",
                        name="n")
    service.jotform_guard.ensure_form_exists.return_value = form
    service.delete_jotform_form(form.form_id, user)
    service.jotform_repo.delete_form.assert_called_once_with(form)



@pytest.mark.asyncio
async def test_get_jotform_list_for_credential_checks_ownership(service, user):
    cred = JotformCredential(id=1, business_id=1, label="l", api_key="secret-key")
    service.jotform_guard.ensure_credential_exists.return_value = cred
    service.jotform_api.get_list_forms = MagicMock(return_value=[])
    service.jotform_repo.get_form_by_credential_id.return_value = []

    result = service.get_jotform_list_for_credential(1, user)

    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == []


class TestSaveFieldMappings:
    def test_saves_when_authorized_and_valid(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        mappings = [JotformFieldMapping(form_id=10, target_key="client_name", qid="3", priority=0)]
        jotform_repo.set_field_mappings.return_value = mappings

        result = service.save_field_mappings(form_id=10, mappings=mappings, current_user=current_user)

        jotform_guard.ensure_form_exists.assert_called_once_with(10)
        jotform_guard.ensure_credential_exists.assert_called_once_with(credential.business_id if False else form.credential_id)
        business_guard.ensure_admin_or_owner.assert_called_once_with(credential.business_id, current_user.id)
        jotform_guard.ensure_mapping_valid.assert_called_once_with(mappings)
        jotform_guard.ensure_no_duplicate_qid.assert_called_once_with(mappings)
        jotform_repo.set_field_mappings.assert_called_once()
        assert result == mappings

    def test_raises_when_form_not_found(self, service, jotform_guard, current_user):
        jotform_guard.ensure_form_exists.side_effect = JotformDomainError()

        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=999, mappings=[], current_user=current_user)

    def test_raises_when_not_admin_or_owner(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        business_guard.ensure_admin_or_owner.side_effect = JotformDomainError()

        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=10, mappings=[], current_user=current_user)

    def test_raises_when_mapping_has_invalid_target_key(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_guard.ensure_mapping_valid.side_effect = JotformDomainError()
        bad_mapping = [JotformFieldMapping(form_id=10, target_key="not_a_real_field", qid="3", priority=0)]

        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=10, mappings=bad_mapping, current_user=current_user)

    def test_raises_on_duplicate_qid(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_guard.ensure_no_duplicate_qid.side_effect = JotformDomainError()
        dup_mappings = [
            JotformFieldMapping(form_id=10, target_key="client_name", qid="3", priority=0),
            JotformFieldMapping(form_id=10, target_key="referral_source", qid="3", priority=0),
        ]

        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=10, mappings=dup_mappings, current_user=current_user)

    def test_normalizes_form_id_regardless_of_input(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        # caller passes wrong/mismatched form_id on the mapping objects
        mappings = [JotformFieldMapping(form_id=999, target_key="client_name", qid="3", priority=0)]
        jotform_repo.set_field_mappings.return_value = mappings

        service.save_field_mappings(form_id=10, mappings=mappings, current_user=current_user)

        called_form_id, called_mappings = jotform_repo.set_field_mappings.call_args[0]
        assert called_form_id == 10
        assert all(m.form_id == 10 for m in called_mappings)


# ---------- get_field_mappings ----------

class TestGetFieldMappings:
    def test_returns_mappings_when_authorized(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        expected = [JotformFieldMapping(form_id=10, target_key="client_name", qid="3", priority=0)]
        jotform_repo.get_field_mappings.return_value = expected

        result = service.get_field_mappings(form_id=10, current_user=current_user)

        business_guard.ensure_admin_or_owner.assert_called_once_with(credential.business_id, current_user.id)
        jotform_repo.get_field_mappings.assert_called_once_with(10)
        assert result == expected

    def test_raises_when_not_authorized(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        business_guard.ensure_admin_or_owner.side_effect = JotformDomainError()

        with pytest.raises(JotformDomainError):
            service.get_field_mappings(form_id=10, current_user=current_user)


# ---------- get_submission_field_defs ----------

class TestGetSubmissionFieldDefs:
    def test_returns_static_registry(self, service):
        from app.domain.Jotform.models.jotform_field_mapping import SUBMISSION_FIELDS

        result = service.get_submission_field_defs()

        assert result == SUBMISSION_FIELDS
        assert any(f.key == "appointment_date" for f in result)
        assert any(f.key == "client_name" for f in result)


# ---------- resolve_submission ----------

class TestResolveSubmission:
    def _mapping(self, target_key, qid, priority=0, subkey=None):
        return JotformFieldMapping(form_id=10, target_key=target_key, qid=qid, priority=priority, subkey=subkey)

    def test_resolves_all_required_fields_present(self, service, jotform_repo, form):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("appointment_date", "1"),
            self._mapping("package", "2"),
            self._mapping("client_name", "3"),
        ]
        raw_answers = {
            "1": {"answer": "2026-10-01"},
            "2": {"answer": "Gold Package"},
            "3": {"answer": "Jane Doe"},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["appointment_date"] == "2026-10-01"
        assert result["package"] == "Gold Package"
        assert result["client_name"] == "Jane Doe"
        assert result["referral_source"] is None

    def test_uses_first_non_null_by_priority(self, service, jotform_repo, form, minimal_fields):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_name", "1", priority=0),
            self._mapping("client_name", "2", priority=1),
        ]
        raw_answers = {
            "1": {"answer": ""},          # empty -> skipped
            "2": {"answer": "Jane Doe"},
        }



        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["client_name"] == "Jane Doe"

    def test_stops_at_first_non_null_even_if_later_priority_has_value(self, service, jotform_repo, form, minimal_fields):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_name", "1", priority=0),
            self._mapping("client_name", "2", priority=1),
        ]
        raw_answers = {
            "1": {"answer": "First Answer"},
            "2": {"answer": "Second Answer"},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["client_name"] == "First Answer"

    def test_ignores_priority_order_in_list_and_sorts(self, service, jotform_repo, form, minimal_fields):
        # mappings returned out of order — resolver must sort by priority itself
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_name", "2", priority=1),
            self._mapping("client_name", "1", priority=0),
        ]
        raw_answers = {
            "1": {"answer": "Correct One"},
            "2": {"answer": "Wrong One"},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["client_name"] == "Correct One"

    def test_reads_subkey_from_composite_answer(self, service, jotform_repo, form, minimal_fields_client_source):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_source_location", "1", subkey="city"),
        ]
        raw_answers = {
            "1": {"answer": {"city": "Paris", "country": "France"}},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["client_source_location"] == "Paris"

    def test_missing_qid_in_raw_answers_treated_as_null(self, service, jotform_repo, form, minimal_fields):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_name", "99"),
        ]
        raw_answers = {}  # qid 99 never submitted

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["client_name"] is None

    def test_raises_when_required_field_unmapped(self, service, jotform_repo, form):
        jotform_repo.get_field_mappings.return_value = []  # nothing mapped at all
        raw_answers = {}

        with pytest.raises(JotformDomainError):
            service.resolve_submission(form=form, raw_answers=raw_answers)

    def test_raises_when_required_field_mapped_but_all_answers_empty(self, service, jotform_repo, form):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("client_name", "1"),
        ]
        raw_answers = {"1": {"answer": ""}}

        with pytest.raises(JotformDomainError):
            service.resolve_submission(form=form, raw_answers=raw_answers)

    def test_optional_field_left_null_does_not_raise(self, service, jotform_repo, form):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("appointment_date", "1"),
            self._mapping("package", "2"),
            self._mapping("client_name", "3"),
        ]
        raw_answers = {
            "1": {"answer": "2026-10-01"},
            "2": {"answer": "Gold Package"},
            "3": {"answer": "Jane Doe"},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["add_ons"] is None
        assert result["guest_count"] is None

    def test_empty_list_answer_treated_as_null(self, service, jotform_repo, form, minimal_fields_adds_on_list):
        jotform_repo.get_field_mappings.return_value = [
            self._mapping("add_ons", "1", priority=0),
            self._mapping("add_ons", "2", priority=1),
        ]
        raw_answers = {
            "1": {"answer": []},
            "2": {"answer": ["Extra Album", "Prints"]},
        }

        result = service.resolve_submission(form=form, raw_answers=raw_answers)

        assert result["add_ons"] == ["Extra Album", "Prints"]