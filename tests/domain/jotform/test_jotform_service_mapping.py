# tests/domain/jotform/test_jotform_service_mapping.py
import pytest
from unittest.mock import Mock

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping, SUBMISSION_FIELDS
from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.user.models.user import User


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
def service(business_guard, jotform_guard, jotform_repo):
    return JotformService(
        business_guard=business_guard,
        jotform_guard=jotform_guard,
        package_repo=Mock(),
        member_repo=Mock(),
        jotform_repo=jotform_repo,
        jotform_api=Mock(),
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

def _mapping(target_key="client_name", qid="1", priority=0):
    return JotformFieldMapping(form_id=999, target_key=target_key, qid=qid, priority=priority)


class TestSaveFieldMappings:
    def test_saves_when_authorized_and_valid(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        mappings = [_mapping()]
        jotform_repo.set_field_mappings.return_value = mappings

        result = service.save_field_mappings(form_id=10, mappings=mappings, current_user=current_user)

        business_guard.ensure_admin_or_owner.assert_called_once_with(credential.business_id, current_user.id)
        jotform_guard.ensure_mapping_valid.assert_called_once()
        jotform_guard.ensure_no_duplicate_qid.assert_called_once()
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

    def test_raises_when_mapping_invalid(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_guard.ensure_mapping_valid.side_effect = JotformDomainError()
        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=10, mappings=[_mapping(target_key="bogus")], current_user=current_user)

    def test_raises_on_duplicate_qid(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_guard.ensure_no_duplicate_qid.side_effect = JotformDomainError()
        with pytest.raises(JotformDomainError):
            service.save_field_mappings(form_id=10, mappings=[_mapping(), _mapping()], current_user=current_user)

    def test_normalizes_form_id_on_saved_mappings(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        mismatched = [_mapping()]  # form_id=999 on the object itself
        jotform_repo.set_field_mappings.return_value = mismatched

        service.save_field_mappings(form_id=10, mappings=mismatched, current_user=current_user)

        called_form_id, called_mappings = jotform_repo.set_field_mappings.call_args[0]
        assert called_form_id == 10
        assert all(m.form_id == 10 for m in called_mappings)


class TestGetFieldMappings:
    def test_returns_when_authorized(self, service, jotform_guard, business_guard, jotform_repo, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        expected = [_mapping()]
        jotform_repo.get_field_mappings.return_value = expected

        result = service.get_field_mappings(form_id=10, current_user=current_user)

        jotform_repo.get_field_mappings.assert_called_once_with(10)
        assert result == expected

    def test_raises_when_not_authorized(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        business_guard.ensure_admin_or_owner.side_effect = JotformDomainError()
        with pytest.raises(JotformDomainError):
            service.get_field_mappings(form_id=10, current_user=current_user)


class TestGetSubmissionFieldDefs:
    def test_returns_static_registry(self, service):

        assert service.get_submission_field_defs() == SUBMISSION_FIELDS