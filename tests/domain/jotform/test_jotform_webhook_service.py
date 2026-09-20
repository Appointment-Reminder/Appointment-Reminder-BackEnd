# tests/domain/jotform/test_jotform_webhook_service.py
import pytest
from unittest.mock import Mock

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformCredential
from app.domain.Jotform.service.jotform_webhook_service import JotformWebhookService
from app.domain.Jotform.service.jotform_submission_assembler import ResolvedBookingContext


@pytest.fixture
def jotform_guard():
    return Mock()

@pytest.fixture
def jotform_service():
    return Mock()

@pytest.fixture
def package_guard():
    return Mock()

@pytest.fixture
def business_guard():
    return Mock()

@pytest.fixture
def member_repo():
    return Mock()

@pytest.fixture
def price_repo():
    return Mock()

@pytest.fixture
def appointment_repo():
    return Mock()

@pytest.fixture
def service(jotform_guard, jotform_service, package_guard, business_guard, member_repo, price_repo, appointment_repo):
    return JotformWebhookService(
        jotform_guard=jotform_guard, jotform_service=jotform_service, package_guard=package_guard,
        business_guard=business_guard, member_repo=member_repo, price_repo=price_repo,
        appointment_repo=appointment_repo,
    )

@pytest.fixture
def form():
    return JotformForm(id=10, form_id="ext-1", name="Booking", credential_id=5)

@pytest.fixture
def credential():
    return JotformCredential(id=5, business_id=100, label="main", api_key="key")

RAW_REQUEST = {"q3_name": {"first": "John", "last": "Smith"}, "q69_email": "john@example.com"}


class TestProcessSubmission:
    def test_fully_resolvable_creates_pending_appointment(
        self, service, jotform_guard, jotform_service, package_guard, member_repo,
        price_repo, appointment_repo, form, credential
    ):
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {
            "client_name": "John", "package": "Gold Package", "appointment_date": "2026-07-31 11:00",
        }
        from unittest.mock import patch
        with patch(
            "app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context",
            return_value=ResolvedBookingContext(
                package_id=1, category_id=2, member_id=7, package_price_id=1,
                price_at_booking=500.0, deposit_amount=100.0, remaining_amount=400.0,
                commission_percent_at_booking=10.0, commission_amount_at_booking=50.0,
                is_personal=False, fully_resolved=True,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "pending"
            assert result.user_id == 7
            assert result.package_id == 1
            assert result.price_at_booking == 500.0

    def test_unresolvable_package_creates_needs_assignment(
        self, service, jotform_guard, jotform_service, package_guard, member_repo,
        price_repo, appointment_repo, form, credential
    ):
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {
            "client_name": "John", "package": "Unknown Package", "appointment_date": "2026-07-31 11:00",
        }
        from unittest.mock import patch
        with patch(
            "app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context",
            return_value=ResolvedBookingContext(
                package_id=None, category_id=None, member_id=None, package_price_id=None,
                price_at_booking=None, deposit_amount=None, remaining_amount=None,
                commission_percent_at_booking=None, commission_amount_at_booking=None,
                is_personal=None, fully_resolved=False,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "needs_assignment"
            assert result.user_id is None
            assert result.price_at_booking is None

    def test_ambiguous_assignment_creates_needs_assignment_with_package_set(
        self, service, jotform_guard, jotform_service, appointment_repo, form, credential
    ):
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {
            "client_name": "John", "package": "Gold Package", "appointment_date": "2026-07-31 11:00",
        }
        from unittest.mock import patch
        with patch(
            "app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context",
            return_value=ResolvedBookingContext(
                package_id=1, category_id=2, member_id=None, package_price_id=None,
                price_at_booking=None, deposit_amount=None, remaining_amount=None,
                commission_percent_at_booking=None, commission_amount_at_booking=None,
                is_personal=None, fully_resolved=False,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "needs_assignment"
            assert result.package_id == 1
            assert result.user_id is None

    def test_invalid_token_raises(self, service, jotform_guard):
        jotform_guard.ensure_webhook_token_valid.side_effect = JotformDomainError()
        with pytest.raises(JotformDomainError):
            service.process_submission(webhook_token="bad-token", raw_request=RAW_REQUEST)