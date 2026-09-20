# tests/domain/jotform/test_refresh_form_questions.py
import pytest
from unittest.mock import Mock, AsyncMock

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential, JotformQuestion
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
def jotform_api():
    return Mock()

@pytest.fixture
def service(business_guard, jotform_guard, jotform_repo, jotform_api):
    return JotformService(
        business_guard=business_guard, jotform_guard=jotform_guard, package_repo=Mock(),
        member_repo=Mock(), jotform_repo=jotform_repo, jotform_api=jotform_api,
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


class TestRefreshFormQuestions:
    @pytest.mark.asyncio
    async def test_authorized_fetches_and_persists(self, service, jotform_guard, business_guard, jotform_repo, jotform_api, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        questions = [JotformQuestion(id="3", name="Name")]
        jotform_api.get_form_questions = AsyncMock(return_value=questions)

        result = await service.refresh_form_question(form_id=10, current_user=current_user)

        jotform_api.get_form_questions.assert_called_once_with(form.form_id, credential.api_key)
        jotform_repo.update_form.assert_called_once()
        assert result.questions == questions

    @pytest.mark.asyncio
    async def test_rejects_when_not_admin_or_owner(self, service, jotform_guard, business_guard, form, credential, current_user):
        jotform_guard.ensure_form_exists.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        business_guard.ensure_admin_or_owner.side_effect = JotformDomainError()

        with pytest.raises(JotformDomainError):
            await service.refresh_form_question(form_id=10, current_user=current_user)