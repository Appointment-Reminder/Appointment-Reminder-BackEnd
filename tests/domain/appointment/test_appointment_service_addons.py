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
        appointment_addon_repo=addon_repo, appointment_addon_service=Mock(),
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


class TestAddonCommissionFollowsTheAssignedMember:
    @pytest.fixture
    def addon_service(self):
        return Mock()

    @pytest.fixture
    def member_service(self, appointment_repo, addon_repo, addon_service):
        business_guard = Mock()
        business_guard.ensure_is_a_member.return_value = Mock(id=1, role=MemberRole.OWNER)
        member_repo = Mock()
        member_repo.get_member_by_id.side_effect = lambda member_id: Mock(id=member_id, business_id=100)
        member_repo.get_member.return_value = Mock(id=1, role=MemberRole.OWNER)
        appointment_repo.get_appointment_by_id.side_effect = lambda appointment_id, **kw: _appointment(appointment_id)
        appointment_repo.update.side_effect = lambda appointment, appointment_id: _appointment(appointment_id)
        appointment_repo.update_status.side_effect = lambda a: a
        return AppointmentService(
            appointment_repo=appointment_repo, business_member_repo=member_repo, business_guard=business_guard,
            appointment_addon_repo=addon_repo, appointment_addon_service=addon_service,
        )

    def test_assigning_another_member_recomputes_the_addon_commission(self, member_service, addon_service):
        member_service.update_single_appointment(100, 1, Mock(member_id=8), Mock(id=9))

        addon_service.assign_member.assert_called_once()
        found, member_id = addon_service.assign_member.call_args.args
        assert (found.id, member_id) == (1, 8)

    def test_keeping_the_same_member_changes_nothing(self, member_service, addon_service):
        member_service.update_single_appointment(100, 1, Mock(member_id=7), Mock(id=9))

        addon_service.assign_member.assert_not_called()

    def test_an_update_without_a_member_changes_nothing(self, member_service, addon_service):
        member_service.update_single_appointment(100, 1, Mock(member_id=None), Mock(id=9))

        addon_service.assign_member.assert_not_called()

    def test_the_unassign_event_clears_the_addon_commission(self, member_service, addon_service):
        from unittest.mock import patch
        from app.domain.appointment.models.appointment_state_machine import AppointmentEvent

        with patch.object(Appointment, "handle"):
            member_service.advance(100, 1, AppointmentEvent.UNASSIGN, Mock(id=9))

        addon_service.unassign_member.assert_called_once()

    def test_other_events_leave_the_addon_commission_alone(self, member_service, addon_service):
        from unittest.mock import patch
        from app.domain.appointment.models.appointment_state_machine import AppointmentEvent

        with patch.object(Appointment, "handle"):
            member_service.advance(100, 1, AppointmentEvent.PHOTOSHOOT, Mock(id=9))

        addon_service.unassign_member.assert_not_called()
