# tests/test_jotform_service.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime

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
    data = JotformForm(credential_id=99, category_id=1, form_id="f1",
                        name="n", member_assigns=[], field_mapping=[])

    with pytest.raises(JotformDomainError):
        service.jotform_form_create(data, user)


def test_form_create_success(service, user):
    cred = JotformCredential(id=1, business_id=1, label="l", api_key="k")
    service.jotform_guard.ensure_credential_exists.return_value = cred
    data = JotformForm(credential_id=1, category_id=2, form_id="f1",
                        name="n", member_assigns=[1], field_mapping=[{"qid": "1"}])
    service.jotform_repo.create_form.return_value = data

    result = service.jotform_form_create(data, user)

    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == data


def test_get_form_by_id_checks_business_membership(service, user):
    form = JotformForm(id=10, credential_id=1, category_id=2, form_id="f1",
                        name="n", member_assigns=[], field_mapping=[])
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
    form = JotformForm(id=10, credential_id=1, category_id=2, form_id="f1",
                        name="n", member_assigns=[], field_mapping=[])
    service.jotform_guard.ensure_form_exists.return_value = form



@pytest.mark.asyncio
async def test_get_jotform_list_for_credential_checks_ownership(service, user):
    cred = JotformCredential(id=1, business_id=1, label="l", api_key="secret-key")
    service.jotform_guard.ensure_credential_exists.return_value = cred
    service.jotform_api.get_list_forms = MagicMock(return_value=[])

    async def fake_forms(api_key):
        assert api_key == "secret-key"
        return []
    service.jotform_api.get_list_forms = fake_forms

    result = await service.get_jotform_list_for_credential(1, user)

    service.business_guard.ensure_admin_or_owner.assert_called_once_with(1, user.id)
    assert result == []