# tests/domain/addon/appointment_addons/test_commission_on_assignment.py
"""Seam 1: Add-on commission follows the member assigned to the appointment."""
import pytest

from app.domain.appointment.models.appointment_state_machine import AppointmentStatus


@pytest.fixture
def unassigned(appointment):
    appointment.member_id = None
    appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
    return appointment


@pytest.fixture
def booked(service, catalogue, unassigned, user):
    """An unassigned appointment holding a percentage add-on, a flat add-on (x3) and a never-paid add-on."""
    catalogue.add(1, price=50)
    catalogue.add(2, price=20, has_quantity=True)
    catalogue.add(3, price=10)
    service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
    service.add_addon(100, 1, addon_id=2, quantity=3, current_user=user)
    service.add_addon(100, 1, addon_id=3, quantity=1, current_user=user)
    return unassigned


def _line(lines, addon_id):
    return lines.get(1, addon_id)


class TestWithoutAMember:
    def test_the_addon_commission_is_unset_not_zero(self, booked, lines):
        for addon_id in (1, 2, 3):
            line = _line(lines, addon_id)
            assert (line.unit_commission_percent, line.unit_commission_amount, line.commission_total) == (None, None, None)

    def test_the_appointment_commission_only_carries_the_package_commission(self, booked):
        assert booked.commission_amount_at_booking == 50.0


class TestAssigning:
    @pytest.fixture(autouse=True)
    def _rates(self, catalogue):
        catalogue.commission(7, 1, 10, pct=True)      # 10% of 50   -> 5
        catalogue.commission(7, 2, 4, pct=False)      # 4 per unit  -> 12 for x3
        catalogue.commission(8, 1, 20, pct=True)      # another member: 20% of 50 -> 10
        # addon 3: no row for any member

    def test_assigning_computes_the_commission_of_each_appointment_addon(self, service, booked, lines):
        service.assign_member(booked, 7)

        assert (_line(lines, 1).unit_commission_percent, _line(lines, 1).commission_total) == (10.0, 5.0)
        assert (_line(lines, 2).unit_commission_amount, _line(lines, 2).commission_total) == (4.0, 12.0)

    def test_a_member_with_no_row_for_an_addon_contributes_zero_for_it(self, service, booked, lines):
        service.assign_member(booked, 7)

        line = _line(lines, 3)
        assert (line.unit_commission_amount, line.unit_commission_percent, line.commission_total) == (0.0, None, 0.0)

    def test_the_commission_is_folded_into_the_appointment_total_and_the_member_is_set(
        self, service, booked, appointment_repo
    ):
        service.assign_member(booked, 7)

        assert booked.member_id == 7
        assert booked.commission_amount_at_booking == 50.0 + 5.0 + 12.0 + 0.0
        appointment_repo.update_totals.assert_called_with(booked)

    def test_the_result_exposes_the_refreshed_addon_rows(self, service, booked):
        result = service.assign_member(booked, 7)

        assert [l.commission_total for l in result.addons] == [5.0, 12.0, 0.0]

    def test_reassigning_replaces_the_previous_members_commission(self, service, booked, lines):
        service.assign_member(booked, 7)
        service.assign_member(booked, 8)

        assert _line(lines, 1).commission_total == 10.0
        assert (_line(lines, 2).commission_total, _line(lines, 3).commission_total) == (0.0, 0.0)
        assert booked.commission_amount_at_booking == 50.0 + 10.0

    def test_assigning_does_not_touch_price_or_duration(self, service, booked):
        before = (booked.price_at_booking, booked.remaining_amount, booked.appointment_duration)

        service.assign_member(booked, 7)

        assert (booked.price_at_booking, booked.remaining_amount, booked.appointment_duration) == before

    def test_an_appointment_without_addons_only_gets_its_member(self, service, appointment, unassigned):
        service.assign_member(unassigned, 7)

        assert unassigned.member_id == 7
        assert unassigned.commission_amount_at_booking == 50.0

    def test_the_commission_starts_from_zero_when_the_appointment_has_none_yet(self, service, booked):
        booked.commission_amount_at_booking = None

        service.assign_member(booked, 7)

        assert booked.commission_amount_at_booking == 17.0

    def test_the_frozen_unit_price_is_used_not_the_current_catalogue_price(self, service, catalogue, booked, lines):
        catalogue.reprice(1, 500)

        service.assign_member(booked, 7)

        assert _line(lines, 1).commission_total == 5.0


class TestUnassigning:
    @pytest.fixture
    def assigned(self, service, catalogue, booked):
        catalogue.commission(7, 1, 10, pct=True)
        catalogue.commission(7, 2, 4, pct=False)
        service.assign_member(booked, 7)
        return booked

    def test_unassigning_clears_the_addon_commission(self, service, assigned, lines):
        service.unassign_member(assigned)

        for addon_id in (1, 2, 3):
            line = _line(lines, addon_id)
            assert (line.unit_commission_percent, line.unit_commission_amount, line.commission_total) == (None, None, None)

    def test_the_appointment_total_drops_back_and_the_member_is_cleared(self, service, assigned, appointment_repo):
        service.unassign_member(assigned)

        assert assigned.member_id is None
        assert assigned.commission_amount_at_booking == 50.0
        appointment_repo.update_totals.assert_called_with(assigned)

    def test_quantity_changes_after_unassigning_keep_the_commission_unset(self, service, assigned, lines, user):
        service.unassign_member(assigned)

        service.set_quantity(100, 1, addon_id=2, quantity=5, current_user=user)

        assert _line(lines, 2).commission_total is None
        assert assigned.commission_amount_at_booking == 50.0

    def test_reassigning_after_unassigning_computes_it_again(self, service, assigned, lines):
        service.unassign_member(assigned)

        service.assign_member(assigned, 7)

        assert _line(lines, 1).commission_total == 5.0
        assert assigned.commission_amount_at_booking == 67.0


class TestUnassigningWithoutAPackageCommission:
    def test_the_commission_total_goes_back_to_unset_not_zero(self, service, catalogue, booked):
        booked.commission_amount_at_booking = None     # needs_assignment: nothing was ever computed
        catalogue.commission(7, 1, 10, pct=True)
        service.assign_member(booked, 7)
        assert booked.commission_amount_at_booking == 5.0

        service.unassign_member(booked)

        assert booked.commission_amount_at_booking is None
