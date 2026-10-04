# tests/domain/addon/appointment_addons/test_resolve_unresolved_addon.py
"""Seam 1: staff resolve an Unresolved Add-on by picking an Add-on from the catalogue."""
import pytest
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError, NoAddonPriceInEffect
from app.domain.addon.models.unresolved_addon import UnresolvedAddon
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.errors.business_errors import BusinessError


@pytest.fixture
def unresolved(lines):
    return lines.add_unresolved_addon(UnresolvedAddon(appointment_id=1, raw_label="10 extra pics pls"))


def _totals(a):
    return (a.price_at_booking, a.remaining_amount, a.commission_amount_at_booking, a.appointment_duration)


class TestResolveUnresolvedAddon:
    def test_resolving_creates_an_appointment_addon_priced_at_resolution_time(
        self, service, catalogue, unresolved, user
    ):
        catalogue.add(1, price=50)
        catalogue.reprice(1, 65)

        result = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        line = result.addons[0]
        assert (line.addon_id, line.unit_price, line.price_total, line.quantity) == (1, 65.0, 65.0, 1)
        assert line.appointment_id == 1

    def test_the_assigned_members_commission_at_resolution_time_is_frozen(
        self, service, catalogue, unresolved, user
    ):
        catalogue.add(1, price=50).commission(7, 1, 10, pct=True)

        line = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user).addons[0]

        assert (line.unit_commission_percent, line.commission_total) == (10.0, 5.0)

    def test_without_an_assigned_member_the_commission_stays_unset(
        self, service, catalogue, appointment, unresolved, user
    ):
        appointment.member_id = None
        appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
        catalogue.add(1, price=50)

        line = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user).addons[0]

        assert line.commission_total is None
        assert appointment.commission_amount_at_booking == 50.0

    def test_the_raw_label_is_kept_for_audit(self, service, catalogue, lines, unresolved, user):
        catalogue.add(1, price=50)

        result = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert result.addons[0].raw_label == "10 extra pics pls"
        stored = lines.get_unresolved_addon(unresolved.id)
        assert stored.raw_label == "10 extra pics pls"
        assert stored.resolved_addon_id == 1
        assert stored.is_resolved

    def test_totals_and_duration_include_the_resolved_addon(
        self, service, catalogue, appointment, appointment_repo, unresolved, user
    ):
        catalogue.add(1, price=50, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)

        service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert _totals(appointment) == (550.0, 450.0, 55.0, 90)
        assert appointment.deposit_amount == 100.0
        appointment_repo.update_totals.assert_called_with(appointment)

    def test_the_appointment_no_longer_reports_it_as_unresolved(self, service, catalogue, unresolved, user):
        catalogue.add(1, price=50)

        result = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert result.unresolved_addons == []

    def test_other_unresolved_addons_stay_pending(self, service, catalogue, lines, unresolved, user):
        other = lines.add_unresolved_addon(UnresolvedAddon(appointment_id=1, raw_label="something else"))
        catalogue.add(1, price=50)

        result = service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert [u.id for u in result.unresolved_addons] == [other.id]

    def test_resolving_onto_an_addon_already_on_the_appointment_is_rejected(
        self, service, catalogue, appointment, lines, unresolved, user
    ):
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        before = _totals(appointment)

        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert _totals(appointment) == before
        assert not lines.get_unresolved_addon(unresolved.id).is_resolved
        assert len(lines.lines) == 1

    @pytest.mark.parametrize("status", ["completed", "canceled", "refunded"])
    def test_resolving_on_a_closed_appointment_is_rejected(
        self, service, catalogue, appointment, lines, unresolved, user, status
    ):
        catalogue.add(1, price=50)
        appointment.status = AppointmentStatus(status)

        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        assert lines.lines == []
        assert not lines.get_unresolved_addon(unresolved.id).is_resolved

    def test_an_addon_with_no_price_in_effect_is_rejected(self, service, catalogue, lines, unresolved, user):
        catalogue.add(1, price=None)

        with pytest.raises(NoAddonPriceInEffect):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)
        assert not lines.get_unresolved_addon(unresolved.id).is_resolved

    def test_an_inactive_addon_is_rejected(self, service, catalogue, unresolved, user):
        catalogue.add(1, price=50, is_active=False)
        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

    def test_an_unresolved_addon_of_another_appointment_is_rejected(self, service, catalogue, lines, user):
        catalogue.add(1, price=50)
        foreign = lines.add_unresolved_addon(UnresolvedAddon(appointment_id=2, raw_label="x"))

        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, foreign.id, addon_id=1, current_user=user)

    def test_an_unknown_unresolved_addon_is_rejected(self, service, catalogue, user):
        catalogue.add(1, price=50)
        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, 999, addon_id=1, current_user=user)

    def test_an_already_resolved_unresolved_addon_cannot_be_resolved_twice(
        self, service, catalogue, unresolved, user
    ):
        catalogue.add(1, price=50).add(2, price=20)
        service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)

        with pytest.raises(AddonError):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=2, current_user=user)

    def test_a_non_member_is_rejected(self, service, catalogue, business_guard, unresolved, user):
        catalogue.add(1, price=50)
        business_guard.ensure_is_a_member.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.resolve_unresolved_addon(100, 1, unresolved.id, addon_id=1, current_user=user)
