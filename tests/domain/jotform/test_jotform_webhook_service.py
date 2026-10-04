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
def addon_resolver():
    return Mock()

@pytest.fixture
def appointment_addon_repo():
    return Mock()

@pytest.fixture
def service(jotform_guard, jotform_service, package_guard, business_guard, member_repo, price_repo, appointment_repo,
            addon_resolver, appointment_addon_repo):
    return JotformWebhookService(
        jotform_guard=jotform_guard, jotform_service=jotform_service, package_guard=package_guard,
        business_guard=business_guard, member_repo=member_repo, price_repo=price_repo,
        appointment_repo=appointment_repo, addon_resolver=addon_resolver,
        appointment_addon_repo=appointment_addon_repo,
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
                package_duration=60,
                package_id=1, category_id=2, member_id=7, package_price_id=1,
                price_at_booking=500.0, deposit_amount=100.0, remaining_amount=400.0,
                commission_percent_at_booking=10.0, commission_amount_at_booking=50.0,
                fully_resolved=True,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "pending"
            assert result.member_id == 7
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
                package_duration=60,
                package_id=None, category_id=None, member_id=None, package_price_id=None,
                price_at_booking=None, deposit_amount=None, remaining_amount=None,
                commission_percent_at_booking=None, commission_amount_at_booking=None,
                fully_resolved=False,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "needs_assignment"
            assert result.member_id is None
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
                package_duration=60,
                package_id=1, category_id=2, member_id=None, package_price_id=None,
                price_at_booking=None, deposit_amount=None, remaining_amount=None,
                commission_percent_at_booking=None, commission_amount_at_booking=None,
                fully_resolved=False,
            ),
        ):
            appointment_repo.create.side_effect = lambda a: a

            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

            assert result.status == "needs_assignment"
            assert result.package_id == 1
            assert result.member_id is None

    def test_invalid_token_raises(self, service, jotform_guard):
        jotform_guard.ensure_webhook_token_valid.side_effect = JotformDomainError()
        with pytest.raises(JotformDomainError):
            service.process_submission(webhook_token="bad-token", raw_request=RAW_REQUEST)

@pytest.fixture
def no_state_machine():
    """These tests are about add-on persistence, not status transitions."""
    from unittest.mock import patch
    from app.domain.appointment.models.appointment_model import Appointment
    with patch.object(Appointment, "handle"):
        yield


@pytest.mark.usefixtures("no_state_machine")
class TestProcessSubmissionAddons:
    def _booking(self, addons, addon_duration=0):
        return ResolvedBookingContext(
            package_duration=60, package_id=1, category_id=2, member_id=7, package_price_id=1,
            price_at_booking=550.0, deposit_amount=100.0, remaining_amount=450.0,
            commission_percent_at_booking=10.0, commission_amount_at_booking=55.0,
            fully_resolved=True, addons=addons, addon_duration=addon_duration,
        )

    def _line(self, addon_id=1):
        from app.domain.addon.models.appointment_addon import AppointmentAddon
        return AppointmentAddon(
            addon_id=addon_id, addon_price_id=10, quantity=1, unit_price=50.0, unit_duration=30,
            unit_commission_percent=10.0, unit_commission_amount=None, price_total=50.0, commission_total=5.0)

    def test_addon_rows_are_saved_against_the_created_appointment(
        self, service, jotform_guard, jotform_service, appointment_repo, appointment_addon_repo, addon_resolver,
        form, credential
    ):
        from unittest.mock import patch
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {"package": "Gold Package", "add_ons": ["Extra"]}
        appointment_repo.create.side_effect = lambda a: setattr(a, "id", 42) or a
        appointment_addon_repo.add.side_effect = lambda line: line

        with patch("app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context",
                   return_value=self._booking([self._line(1), self._line(2)], addon_duration=60)) as resolve:
            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

        assert resolve.call_args.kwargs["addon_labels"] == ["Extra"]
        assert resolve.call_args.kwargs["addon_resolver"] is addon_resolver
        assert [l.appointment_id for l in result.addons] == [42, 42]
        assert appointment_addon_repo.add.call_count == 2
        assert result.appointment_duration == 120   # 60 package + 60 add-ons
        assert result.price_at_booking == 550.0

    def test_a_submission_without_addons_saves_no_rows(
        self, service, jotform_guard, jotform_service, appointment_repo, appointment_addon_repo, form, credential
    ):
        from unittest.mock import patch
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {"package": "Gold Package"}
        appointment_repo.create.side_effect = lambda a: a

        with patch("app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context",
                   return_value=self._booking([])):
            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

        assert result.addons == []
        appointment_addon_repo.add.assert_not_called()


@pytest.mark.usefixtures("no_state_machine")
class TestProcessSubmissionUnresolvedAddons:
    def test_unresolved_labels_are_saved_on_the_created_appointment(
        self, service, jotform_guard, jotform_service, appointment_repo, appointment_addon_repo, form, credential
    ):
        from unittest.mock import patch
        jotform_guard.ensure_webhook_token_valid.return_value = form
        jotform_guard.ensure_credential_exists.return_value = credential
        jotform_service.resolve_submission.return_value = {"package": "Gold Package", "add_ons": ["Mystery"]}
        appointment_repo.create.side_effect = lambda a: setattr(a, "id", 42) or a
        appointment_addon_repo.add_unresolved_addon.side_effect = lambda u: u

        booking = ResolvedBookingContext(
            package_duration=60, package_id=1, category_id=2, member_id=7, package_price_id=1,
            price_at_booking=500.0, deposit_amount=100.0, remaining_amount=400.0,
            commission_percent_at_booking=10.0, commission_amount_at_booking=50.0,
            fully_resolved=True, unresolved_addon_labels=["Mystery"],
        )
        with patch("app.domain.Jotform.service.jotform_webhook_service.resolve_booking_context", return_value=booking):
            result = service.process_submission(webhook_token="tok-123", raw_request=RAW_REQUEST)

        assert [(u.appointment_id, u.raw_label) for u in result.unresolved_addons] == [(42, "Mystery")]
