# tests/domain/overview/test_period_income.py
"""Income derived from frozen amounts, status and dates (ADR 0002), and who may ask."""
import pytest
from datetime import date, datetime, timezone

from app.domain.appointment.models.appointment_state_machine import AppointmentStatus as S
from app.domain.business.errors.business_errors import BusinessError, UnauthorizedBusinessAction
from app.domain.business.models.business_member_model import MemberRole
from app.domain.overview.errors.overview_errors import InvalidPeriod
from tests.domain.overview.conftest import appointment, line


def figures(overview, **kw):
    return overview(**kw).business


class TestIncomeFigures:
    def test_worked_example_deposit_on_booking_and_balance_on_the_shoot(self, read, overview):
        read.appointments = [appointment()]

        b = figures(overview)

        assert (b.deposit_income, b.balance_income, b.total_income) == (50, 200, 250)
        assert (b.commission_payable, b.owner_take) == (70, 180)

    def test_deposit_and_balance_are_dated_separately(self, read, overview):
        read.appointments = [appointment(booked=datetime(2026, 9, 20), on=datetime(2026, 10, 10))]

        b = figures(overview)
        assert (b.deposit_income, b.balance_income) == (0, 200)

        read.appointments = [appointment(booked=datetime(2026, 10, 2), on=datetime(2026, 11, 20, 10))]
        b = figures(overview)
        assert (b.deposit_income, b.balance_income, b.outstanding_balance) == (50, 0, 0)

    def test_a_canceled_appointment_keeps_only_its_retained_deposit(self, read, overview):
        read.appointments = [appointment(status=S.CANCELED)]

        b = figures(overview)

        assert (b.deposit_income, b.balance_income, b.outstanding_balance) == (50, 0, 0)
        assert (b.booked_revenue, b.appointments_made, b.commission_payable) == (0, 0, 0)

    def test_a_refunded_appointment_counts_for_nothing(self, read, overview):
        read.appointments = [appointment(status=S.REFUNDED)]

        b = figures(overview)

        assert (b.total_income, b.booked_revenue, b.appointments_made, b.outstanding_balance) == (0, 0, 0, 0)

    def test_a_future_appointment_is_outstanding_balance_and_owes_no_commission_yet(self, read, overview):
        read.appointments = [appointment(on=datetime(2026, 10, 25, 10))]

        b = figures(overview)

        assert (b.deposit_income, b.balance_income, b.outstanding_balance) == (50, 0, 200)
        assert b.commission_payable == 0

    def test_booked_revenue_and_appointments_made_count_by_booking_date(self, read, overview):
        read.appointments = [appointment(on=datetime(2026, 12, 1)), appointment(booked=datetime(2026, 9, 1))]

        b = figures(overview)

        assert (b.booked_revenue, b.appointments_made) == (250, 1)

    def test_an_empty_period_returns_zeros(self, overview):
        b = figures(overview)

        assert (b.total_income, b.deposit_income, b.balance_income, b.outstanding_balance, b.booked_revenue,
                b.appointments_made, b.commission_payable, b.owner_take) == (0, 0, 0, 0, 0, 0, 0, 0)

    def test_money_is_rounded_to_cents(self, read, overview):
        read.appointments = [appointment(price=100.0, deposit=33.333, commission=0)]
        read.appointments[0].remaining_amount = 66.667

        b = figures(overview)

        assert (b.deposit_income, b.balance_income, b.total_income) == (33.33, 66.67, 100.0)


class TestPeriodDays:
    def test_the_to_day_is_included_in_full(self, read, overview):
        read.appointments = [appointment(booked=datetime(2026, 10, 31, 23, 59))]

        assert figures(overview).deposit_income == 50

    def test_a_booking_just_after_midnight_paris_lands_on_the_paris_day(self, read, overview):
        # 2026-10-31 23:30 UTC is 2026-11-01 00:30 in Paris (CET after the DST change on the 25th).
        read.appointments = [appointment(booked=datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc))]

        assert figures(overview).deposit_income == 0
        assert figures(overview, period=(date(2026, 11, 1), date(2026, 11, 30))).deposit_income == 50

    def test_the_first_day_starts_at_midnight_paris(self, read, overview):
        # 2026-09-30 22:30 UTC is 2026-10-01 00:30 in Paris (CEST).
        read.appointments = [appointment(booked=datetime(2026, 9, 30, 22, 30, tzinfo=timezone.utc))]

        assert figures(overview).deposit_income == 50

    def test_from_after_to_is_rejected(self, overview):
        with pytest.raises(InvalidPeriod):
            overview(period=(date(2026, 10, 5), date(2026, 10, 1)))

    def test_an_unknown_grouping_is_rejected(self, overview):
        with pytest.raises(InvalidPeriod):
            overview(group_by="year")


class TestAddonIncome:
    def test_addon_income_is_part_of_the_balance_income(self, read, overview):
        read.appointments = [appointment(price=330.0, addons=[line(1, 30.0), line(2, 100.0, quantity=2)])]

        b = figures(overview)

        assert (b.addon_income, b.package_balance, b.balance_income) == (130, 150, 280)
        assert b.package_balance + b.addon_income == b.balance_income

    @pytest.mark.parametrize("kw", [dict(status=S.CANCELED), dict(status=S.REFUNDED),
                                    dict(on=datetime(2026, 10, 25))])
    def test_addons_of_canceled_refunded_or_future_appointments_are_not_income(self, read, overview, kw):
        read.appointments = [appointment(price=280.0, addons=[line(1, 30.0)], **kw)]

        assert figures(overview).addon_income == 0


class TestCommissionPayable:
    @pytest.mark.parametrize("kw", [dict(status=S.CANCELED), dict(status=S.REFUNDED),
                                    dict(on=datetime(2026, 10, 25)), dict(member_id=1), dict(member_id=None)])
    def test_owes_nothing_when_canceled_refunded_future_owner_or_unassigned(self, read, overview, kw):
        read.appointments = [appointment(**kw)]

        assert figures(overview).commission_payable == 0

    def test_owner_take_keeps_every_deposit_and_the_owners_own_appointments(self, read, overview):
        read.appointments = [appointment(), appointment(member_id=1, commission=40.0),
                             appointment(status=S.CANCELED)]

        b = figures(overview)

        assert (b.total_income, b.commission_payable, b.owner_take) == (250 + 250 + 50, 70, 480)

    def test_a_commission_larger_than_the_balance_is_reported_as_frozen_and_flagged(self, read, overview):
        read.appointments = [appointment(commission=300.0), appointment()]

        b = figures(overview)

        assert (b.commission_payable, b.commissions_above_balance) == (370, 1)
        assert b.owner_take == 500 - 370

    def test_the_commission_is_read_with_the_current_role_of_the_member(self, read, members, overview):
        read.appointments = [appointment(member_id=7)]
        members[2].role = MemberRole.OWNER  # Paula is now an owner

        assert figures(overview).commission_payable == 0


class TestAccess:
    def test_the_owner_sees_owner_take(self, read, overview):
        read.appointments = [appointment()]

        assert overview().business.owner_take == 180

    def test_an_admin_sees_the_business_without_owner_take(self, read, overview, as_member):
        as_member(2)
        read.appointments = [appointment()]

        result = overview()

        assert result.business.total_income == 250
        assert result.business.owner_take is None

    def test_a_non_member_is_refused(self, overview):
        with pytest.raises(BusinessError):
            overview(business_id=999)

    def test_an_assistant_is_refused(self, members, overview):
        members[0].role = MemberRole.ASSISTANT

        with pytest.raises(UnauthorizedBusinessAction):
            overview()
