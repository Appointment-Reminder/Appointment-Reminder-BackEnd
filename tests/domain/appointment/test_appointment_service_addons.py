# tests/domain/appointment/test_appointment_service_addons.py
import pytest
from datetime import datetime
from unittest.mock import Mock

from app.domain.addon.models.appointment_addon import AppointmentAddon
from app.domain.addon.models.unresolved_addon import UnresolvedAddon
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.appointment.service.appointment_service import AppointmentService
from app.domain.business.models.business_member_model import MemberRole


def _appointment(id):
    return Appointment(
        id=id, business_id=100, member_id=7, form_id=None, package_id=1, package_price_id=1,
        client_first_name="a", client_last_name="b", client_phone=None, client_email=None, referral_source=None,
        price_at_booking=500.0, deposit_amount=100.0, remaining_amount=400.0,
        commission_percent_at_booking=None, commission_amount_at_booking=None,
        appointment_date=datetime(2026, 10, 4), appointment_location=None, appointment_duration=60,
        appointment_note=None, number_of_persons=None, privacy_opt_out=None,
        status=AppointmentStatus.PENDING, created_at=datetime(2026, 10, 1), updated_at=datetime(2026, 10, 1),
    )


@pytest.fixture
def addon_repo():
    repo = Mock()
    repo.list_for_appointments.return_value = {}
    repo.list_unresolved_for_appointments.return_value = {}
    repo.appointment_ids_with_unresolved.return_value = {2}
    return repo


@pytest.fixture
def appointment_repo():
    repo = Mock()
    repo.find_by_business.return_value = [_appointment(1), _appointment(2)]
    return repo


@pytest.fixture
def service(appointment_repo, addon_repo):
    business_guard = Mock()
    business_guard.ensure_is_a_member.return_value = Mock(id=7, role=MemberRole.OWNER)
    return AppointmentService(
        appointment_repo=appointment_repo, business_member_repo=Mock(), business_guard=business_guard,
        appointment_addon_repo=addon_repo,
    )


class TestAppointmentsExposeAddons:
    def test_appointments_carry_their_addon_rows_and_unresolved_addons(self, service, addon_repo):
        line = Mock(spec=AppointmentAddon)
        pending = UnresolvedAddon(id=5, appointment_id=2, raw_label="Mystery")
        addon_repo.list_for_appointments.return_value = {1: [line]}
        addon_repo.list_unresolved_for_appointments.return_value = {2: [pending]}

        first, second = service.get_appointments_by_business(100, Mock(id=9))

        assert first.addons == [line] and first.unresolved_addons == []
        assert second.addons == [] and second.unresolved_addons == [pending]


class TestFilterByUnresolvedAddons:
    def test_only_appointments_with_unresolved_addons(self, service):
        result = service.get_appointments_by_business(100, Mock(id=9), has_unresolved_addons=True)
        assert [a.id for a in result] == [2]

    def test_only_appointments_without_unresolved_addons(self, service):
        result = service.get_appointments_by_business(100, Mock(id=9), has_unresolved_addons=False)
        assert [a.id for a in result] == [1]

    def test_no_filter_returns_everything(self, service):
        assert [a.id for a in service.get_appointments_by_business(100, Mock(id=9))] == [1, 2]
