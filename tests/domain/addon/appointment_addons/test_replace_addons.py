# tests/domain/addon/appointment_addons/test_replace_addons.py
"""Seam 5: replace the whole set of Appointment Add-ons of an appointment in one all-or-nothing call."""
import pytest

from app.domain.addon.errors.addon_errors import AddonError, AppointmentAddonsLocked, AppointmentNotPriced, \
    NoAddonPriceInEffect
from app.domain.addon.models.unresolved_addon import UnresolvedAddon
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.models.business_member_model import MemberRole

BASE = (500.0, 400.0, 50.0, 60)


def _totals(a):
    return (a.price_at_booking, a.remaining_amount, a.commission_amount_at_booking, a.appointment_duration)


def _replace(service, user, *pairs):
    return service.replace_addons(100, 1, list(pairs), user)


@pytest.fixture
def catalogue(catalogue):
    """Add-ons 1 and 2 cost 50 and 30 with a 10% commission for member 7; 3 is a counted, timed one."""
    catalogue.add(1, price=50).commission(7, 1, 10, pct=True)
    catalogue.add(2, price=30).commission(7, 2, 10, pct=True)
    catalogue.add(3, price=20, has_quantity=True, has_duration=True, duration_minutes=15).commission(7, 3, 2, pct=False)
    return catalogue


class TestReplaceAddons:
    def test_books_the_new_addons_at_todays_price_and_the_members_commission(self, service, lines, appointment, user):
        result = _replace(service, user, (1, 1), (3, 2))

        assert sorted((l.addon_id, l.quantity) for l in result.addons) == [(1, 1), (3, 2)]
        line = next(l for l in result.addons if l.addon_id == 1)
        assert (line.unit_price, line.unit_commission_percent, line.appointment_id) == (50.0, 10.0, 1)
        assert _totals(appointment) == (590.0, 490.0, 59.0, 90)
        assert appointment.deposit_amount == 100.0

    def test_unchanged_lines_keep_their_frozen_price_and_commission(self, service, catalogue, appointment, user):
        service.add_addon(100, 1, 1, 1, user)
        catalogue.reprice(1, 99)
        catalogue.commissions[(7, 1)].clear()
        catalogue.commission(7, 1, 40, pct=True)

        result = _replace(service, user, (1, 1))

        line = result.addons[0]
        assert (line.unit_price, line.unit_commission_percent) == (50.0, 10.0)
        assert _totals(appointment) == (550.0, 450.0, 55.0, 60)

    def test_changes_the_quantity_of_an_existing_line_at_its_frozen_price(self, service, catalogue, appointment, user):
        service.add_addon(100, 1, 3, 1, user)
        catalogue.reprice(3, 99)

        result = _replace(service, user, (3, 4))

        line = result.addons[0]
        assert (line.quantity, line.unit_price, line.price_total) == (4, 20.0, 80.0)
        assert _totals(appointment) == (580.0, 480.0, 58.0, 120)

    def test_removes_the_lines_missing_from_the_body(self, service, appointment, user):
        service.add_addon(100, 1, 1, 1, user)
        service.add_addon(100, 1, 2, 1, user)

        result = _replace(service, user, (2, 1))

        assert [l.addon_id for l in result.addons] == [2]
        assert _totals(appointment) == (530.0, 430.0, 53.0, 60)

    def test_an_empty_list_clears_every_addon_and_restores_the_package_totals(self, service, appointment, user):
        service.add_addon(100, 1, 1, 1, user)
        service.add_addon(100, 1, 3, 2, user)

        result = _replace(service, user)

        assert result.addons == []
        assert _totals(appointment) == BASE

    def test_adds_changes_and_removes_in_one_call(self, service, appointment, user):
        service.add_addon(100, 1, 1, 1, user)
        service.add_addon(100, 1, 3, 1, user)

        result = _replace(service, user, (3, 2), (2, 1))

        assert sorted((l.addon_id, l.quantity) for l in result.addons) == [(2, 1), (3, 2)]
        assert _totals(appointment) == (570.0, 470.0, 57.0, 90)

    def test_changes_are_written_once_together_with_the_totals(self, service, lines, appointment, appointment_repo, user):
        _replace(service, user, (1, 1), (2, 1))

        assert lines.applied == [appointment]
        appointment_repo.update_totals.assert_not_called()

    def test_unresolved_addons_are_left_alone(self, service, lines, user):
        lines.unresolved.append(UnresolvedAddon(appointment_id=1, raw_label="mystery", id=77))

        result = _replace(service, user, (1, 1))

        assert [u.id for u in result.unresolved_addons] == [77]


class TestReplaceAddonsAllOrNothing:
    @pytest.fixture
    def booked(self, service, lines, appointment, user):
        service.add_addon(100, 1, 1, 1, user)
        lines.applied.clear()
        return _totals(appointment), [(l.addon_id, l.quantity) for l in lines.lines]

    def _untouched(self, lines, appointment, booked):
        assert lines.applied == []
        assert _totals(appointment) == booked[0]
        assert [(l.addon_id, l.quantity) for l in lines.lines] == booked[1]

    def test_a_duplicate_addon_is_rejected(self, service, lines, appointment, booked, user):
        with pytest.raises(AddonError):
            _replace(service, user, (2, 1), (2, 1))
        self._untouched(lines, appointment, booked)

    def test_one_inactive_addon_rejects_the_whole_set(self, service, catalogue, lines, appointment, booked, user):
        catalogue.add(4, price=10, is_active=False)

        with pytest.raises(AddonError):
            _replace(service, user, (2, 1), (4, 1))
        self._untouched(lines, appointment, booked)

    def test_one_addon_without_a_price_rejects_the_whole_set(self, service, catalogue, lines, appointment, booked, user):
        catalogue.add(4, price=None)

        with pytest.raises(NoAddonPriceInEffect):
            _replace(service, user, (2, 1), (4, 1))
        self._untouched(lines, appointment, booked)

    @pytest.mark.parametrize("quantity", [0, -1, 2])
    def test_a_bad_quantity_on_an_existing_line_rejects_the_whole_set(
        self, service, lines, appointment, booked, user, quantity
    ):
        # add-on 1 has no quantity, so only 1 is allowed
        with pytest.raises(AddonError):
            _replace(service, user, (2, 1), (1, quantity))
        self._untouched(lines, appointment, booked)

    def test_a_bad_quantity_on_a_new_line_rejects_the_whole_set(self, service, lines, appointment, booked, user):
        with pytest.raises(AddonError):
            _replace(service, user, (1, 1), (2, 3))
        self._untouched(lines, appointment, booked)

    def test_an_addon_of_another_category_rejects_the_whole_set(
        self, service, catalogue, lines, appointment, booked, user
    ):
        catalogue.add(4, price=10, category_id=99)

        with pytest.raises(AddonError):
            _replace(service, user, (2, 1), (4, 1))
        self._untouched(lines, appointment, booked)

    def test_adding_to_an_unpriced_appointment_is_rejected(self, service, lines, appointment, booked, user):
        appointment.price_at_booking = None

        with pytest.raises(AppointmentNotPriced):
            _replace(service, user, (1, 1), (2, 1))
        assert lines.applied == []


class TestReplaceAddonsAccess:
    def test_a_closed_appointment_is_locked(self, service, appointment, lines, user):
        appointment.status = AppointmentStatus.COMPLETED

        with pytest.raises(AppointmentAddonsLocked):
            _replace(service, user, (1, 1))
        assert lines.applied == []

    def test_a_photographer_who_is_not_assigned_is_rejected(self, service, business_guard, lines, user):
        business_guard.ensure_is_a_member.return_value.id = 99
        business_guard.ensure_is_a_member.return_value.role = MemberRole.PHOTOGRAPHER

        with pytest.raises(AddonError):
            _replace(service, user, (1, 1))
        assert lines.applied == []

    def test_the_assigned_photographer_can_replace(self, service, business_guard, user):
        business_guard.ensure_is_a_member.return_value.id = 7
        business_guard.ensure_is_a_member.return_value.role = MemberRole.PHOTOGRAPHER

        assert [l.addon_id for l in _replace(service, user, (1, 1)).addons] == [1]

    def test_an_appointment_of_another_business_is_rejected(self, service, appointment, lines, user):
        appointment.business_id = 555

        with pytest.raises(AddonError):
            _replace(service, user, (1, 1))
        assert lines.applied == []
