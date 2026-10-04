# tests/domain/addon/appointment_addons/test_appointment_addon_edits.py
"""Seam 1: add, remove and change the quantity of Appointment Add-ons on an existing appointment."""
import pytest
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError, NoAddonPriceInEffect
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.models.business_member_model import MemberRole


def _totals(a):
    return (a.price_at_booking, a.remaining_amount, a.commission_amount_at_booking, a.appointment_duration)


class TestAddAddon:
    def test_snapshots_the_current_price_and_the_assigned_members_commission(
        self, service, catalogue, appointment, user
    ):
        catalogue.add(1, price=50).commission(7, 1, 10, pct=True)

        result = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        line = result.addons[0]
        assert (line.addon_id, line.addon_price_id, line.quantity) == (1, 10, 1)
        assert (line.unit_price, line.line_total) == (50.0, 50.0)
        assert (line.unit_commission_percent, line.line_commission) == (10.0, 5.0)
        assert line.appointment_id == 1

    def test_updates_the_appointment_totals_and_persists_them(
        self, service, catalogue, appointment, appointment_repo, user
    ):
        catalogue.add(1, price=50, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)

        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        assert _totals(appointment) == (550.0, 450.0, 55.0, 90)
        assert appointment.deposit_amount == 100.0
        appointment_repo.update_totals.assert_called_with(appointment)

    def test_quantity_scales_the_line(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50, has_quantity=True, has_duration=True, duration_minutes=30).commission(7, 1, 4, pct=False)

        line = service.add_addon(100, 1, addon_id=1, quantity=3, current_user=user).addons[0]

        assert (line.line_total, line.line_commission) == (150.0, 12.0)
        assert _totals(appointment) == (650.0, 550.0, 62.0, 150)

    def test_without_an_assigned_member_the_addon_commission_is_unset(self, service, catalogue, appointment, user):
        appointment.member_id = None
        appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
        catalogue.add(1, price=50).commission(7, 1, 10, pct=True)

        line = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user).addons[0]

        assert (line.unit_commission_percent, line.unit_commission_amount, line.line_commission) == (None, None, None)
        assert appointment.commission_amount_at_booking == 50.0
        assert appointment.price_at_booking == 550.0

    def test_adding_an_addon_already_on_the_appointment_is_rejected(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        assert appointment.price_at_booking == 550.0

    def test_an_addon_with_no_price_in_effect_is_rejected(self, service, catalogue, appointment, user):
        catalogue.add(1, price=None)
        with pytest.raises(NoAddonPriceInEffect):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        catalogue.add(2, price=50, price_days=+5)
        with pytest.raises(NoAddonPriceInEffect):
            service.add_addon(100, 1, addon_id=2, quantity=1, current_user=user)
        assert appointment.price_at_booking == 500.0

    def test_an_inactive_addon_is_rejected(self, service, catalogue, user):
        catalogue.add(1, price=50, is_active=False)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_unknown_addon_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=404, quantity=1, current_user=user)

    def test_an_addon_of_another_business_is_rejected(self, service, catalogue, user):
        catalogue.add(1, price=50, business_id=555)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_quantity_below_one_is_rejected(self, service, catalogue, user, quantity):
        catalogue.add(1, price=50, has_quantity=True)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=quantity, current_user=user)

    def test_quantity_other_than_one_is_rejected_for_an_addon_without_quantity(self, service, catalogue, user):
        catalogue.add(1, price=50, has_quantity=False)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=2, current_user=user)


class TestChangeQuantity:
    @pytest.fixture(autouse=True)
    def _booked(self, service, catalogue, user):
        catalogue.add(1, price=50, has_quantity=True, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)
        catalogue.add(2, price=20, has_quantity=True).commission(7, 2, 4, pct=False)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        service.add_addon(100, 1, addon_id=2, quantity=1, current_user=user)

    def test_doubling_the_quantity_doubles_the_line_and_the_totals(self, service, appointment, user):
        service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)

        assert _totals(appointment) == (620.0, 520.0, 64.0, 120)   # 500+100+20 / 400+120 / 50+10+4 / 60+60

    def test_it_uses_the_frozen_unit_price_even_if_the_catalogue_price_changed(
        self, service, catalogue, appointment, user
    ):
        catalogue.reprice(1, 500)

        line = next(l for l in service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user).addons
                    if l.addon_id == 1)

        assert (line.unit_price, line.line_total, line.addon_price_id) == (50.0, 100.0, 10)
        assert appointment.price_at_booking == 620.0

    def test_a_flat_commission_scales_with_quantity_and_a_percentage_follows_the_line_total(
        self, service, appointment, user
    ):
        result = service.set_quantity(100, 1, addon_id=2, quantity=3, current_user=user)
        flat = next(l for l in result.addons if l.addon_id == 2)
        assert flat.line_commission == 12.0

        result = service.set_quantity(100, 1, addon_id=1, quantity=4, current_user=user)
        percent = next(l for l in result.addons if l.addon_id == 1)
        assert (percent.line_total, percent.line_commission) == (200.0, 20.0)
        assert appointment.commission_amount_at_booking == 50.0 + 20.0 + 12.0

    def test_going_back_down_restores_the_totals(self, service, appointment, user):
        service.set_quantity(100, 1, addon_id=1, quantity=5, current_user=user)
        service.set_quantity(100, 1, addon_id=1, quantity=1, current_user=user)

        assert _totals(appointment) == (570.0, 470.0, 59.0, 90)

    @pytest.mark.parametrize("quantity", [0, -3])
    def test_quantity_below_one_is_rejected_and_nothing_changes(self, service, appointment, lines, user, quantity):
        before = _totals(appointment)
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=1, quantity=quantity, current_user=user)
        assert _totals(appointment) == before
        assert lines.get(1, 1).quantity == 1

    def test_quantity_other_than_one_is_rejected_for_an_addon_without_quantity(
        self, service, catalogue, user
    ):
        catalogue.add(3, price=10, has_quantity=False)
        service.add_addon(100, 1, addon_id=3, quantity=1, current_user=user)

        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=3, quantity=2, current_user=user)

    def test_changing_the_quantity_of_an_addon_not_on_the_appointment_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=99, quantity=2, current_user=user)


class TestRemoveAddon:
    def test_removing_updates_the_totals_and_the_duration(self, service, catalogue, appointment, lines, user):
        catalogue.add(1, price=50, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        result = service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert result.addons == []
        assert lines.lines == []
        assert _totals(appointment) == (500.0, 400.0, 50.0, 60)

    def test_removing_a_quantified_line_removes_all_of_its_units(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50, has_quantity=True).commission(7, 1, 4, pct=False)
        service.add_addon(100, 1, addon_id=1, quantity=3, current_user=user)

        service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert _totals(appointment) == (500.0, 400.0, 50.0, 60)

    def test_remove_then_re_add_takes_the_current_catalogue_price(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        catalogue.reprice(1, 80)

        service.remove_addon(100, 1, addon_id=1, current_user=user)
        line = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user).addons[0]

        assert (line.unit_price, line.addon_price_id) == (80.0, 980)
        assert appointment.price_at_booking == 580.0

    def test_removing_an_addon_not_on_the_appointment_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.remove_addon(100, 1, addon_id=1, current_user=user)

    def test_removal_without_commission_on_the_line_leaves_the_appointment_commission_alone(
        self, service, catalogue, appointment, user
    ):
        appointment.member_id = None
        appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert appointment.commission_amount_at_booking == 50.0


EDITABLE = ["new", "needs_assignment", "pending", "pending_selection", "pending_editing", "pending_review"]
CLOSED = ["completed", "canceled", "refunded"]


class TestStatusGuards:
    @pytest.fixture(autouse=True)
    def _catalogue(self, catalogue):
        catalogue.add(1, price=50, has_quantity=True)

    @pytest.mark.parametrize("status", EDITABLE)
    def test_edits_are_allowed_until_pending_review(self, service, appointment, user, status):
        appointment.status = AppointmentStatus(status)

        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)
        service.remove_addon(100, 1, addon_id=1, current_user=user)

    @pytest.mark.parametrize("status", CLOSED)
    def test_edits_are_rejected_on_closed_appointments(self, service, appointment, lines, user, status):
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        appointment.status = AppointmentStatus(status)
        before = _totals(appointment)

        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)
        with pytest.raises(AddonError):
            service.remove_addon(100, 1, addon_id=1, current_user=user)
        assert _totals(appointment) == before
        assert len(lines.lines) == 1


class TestAccess:
    @pytest.fixture(autouse=True)
    def _catalogue(self, catalogue):
        catalogue.add(1, price=50)

    def test_a_non_member_is_rejected(self, service, business_guard, user):
        business_guard.ensure_is_a_member.side_effect = BusinessError()
        with pytest.raises(BusinessError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_the_assigned_photographer_may_edit(self, service, business_guard, user):
        business_guard.ensure_is_a_member.return_value = Mock(id=7, role=MemberRole.PHOTOGRAPHER)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_another_photographer_may_not_edit(self, service, business_guard, user):
        business_guard.ensure_is_a_member.return_value = Mock(id=8, role=MemberRole.PHOTOGRAPHER)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_appointment_of_another_business_is_not_found(self, service, appointment, user):
        appointment.business_id = 555
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_unknown_appointment_is_not_found(self, service, user):
        with pytest.raises(AddonError):
            service.add_addon(100, 404, addon_id=1, quantity=1, current_user=user)


class TestCategoryRestriction:
    """The fixture package belongs to category 2."""

    def test_an_addon_restricted_to_the_package_category_can_be_added(self, service, catalogue, user):
        catalogue.add(1, price=50, category_id=2)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_addon_restricted_to_another_category_is_rejected(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50, category_id=99)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        assert appointment.price_at_booking == 500.0

    def test_an_unrestricted_addon_fits_any_package(self, service, catalogue, user):
        catalogue.add(1, price=50, category_id=None)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_a_restricted_addon_is_rejected_when_the_appointment_has_no_package(
        self, service, catalogue, appointment, user
    ):
        appointment.package_id = None
        catalogue.add(1, price=50, category_id=2)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_resolving_onto_a_restricted_addon_of_another_category_is_rejected(
        self, service, catalogue, lines, user
    ):
        from app.domain.addon.models.unresolved_addon import UnresolvedAddon
        catalogue.add(1, price=50, category_id=99)
        pending = lines.add_unresolved(UnresolvedAddon(appointment_id=1, raw_label="x"))
        with pytest.raises(AddonError):
            service.resolve_unresolved(100, 1, pending.id, addon_id=1, current_user=user)
        assert not lines.get_unresolved(pending.id).is_resolved


class TestCommissionRounding:
    def test_a_percentage_commission_is_rounded_to_cents_like_the_totals(self, service, catalogue, appointment, user):
        catalogue.add(1, price=33, has_quantity=True).commission(7, 1, 7, pct=True)   # 2.31 per unit

        line = service.add_addon(100, 1, addon_id=1, quantity=3, current_user=user).addons[0]

        assert line.line_commission == 6.93
        assert appointment.commission_amount_at_booking == 56.93
