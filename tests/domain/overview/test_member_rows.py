# tests/domain/overview/test_member_rows.py
"""Per-photographer rows and what a photographer may see."""
import pytest
from datetime import datetime

from app.domain.appointment.models.appointment_state_machine import AppointmentStatus as S
from app.domain.business.errors.business_errors import BusinessError, UnauthorizedBusinessAction
from tests.domain.overview.conftest import appointment


def rows(result):
    return {r.member_id: r for r in result.members}


class TestRows:
    def test_a_row_per_member_and_an_unassigned_row(self, overview):
        assert sorted(rows(overview()), key=lambda k: (k is None, k)) == [1, 2, 7, 8, None]

    def test_a_row_carries_its_figures(self, read, overview):
        read.appointments = [appointment(price=300.0, commission=70.0), appointment(price=100.0, commission=10.0),
                             appointment(status=S.CANCELED)]

        paula = rows(overview())[7]

        assert (paula.name, paula.income, paula.booked_revenue, paula.commission_earned) == ("Paula", 450, 400, 80)
        assert (paula.appointments_made, paula.average_appointment_value) == (2, 200)
        assert paula.cancellation_rate == pytest.approx(1 / 3)

    def test_a_retained_deposit_is_income_of_the_assigned_member_with_no_commission(self, read, overview):
        read.appointments = [appointment(status=S.CANCELED)]

        paula = rows(overview())[7]

        assert (paula.income, paula.commission_earned, paula.booked_revenue) == (50, 0, 0)

    def test_the_owners_own_row_shows_no_commission(self, read, overview):
        read.appointments = [appointment(member_id=1, commission=40.0)]

        assert rows(overview())[1].commission_earned == 0

    def test_unassigned_appointments_get_their_own_row(self, read, overview):
        read.appointments = [appointment(member_id=None)]

        assert rows(overview())[None].income == 250

    def test_rows_add_up_to_the_business_total(self, read, overview):
        read.appointments = [appointment(), appointment(member_id=8, price=500.0), appointment(member_id=None),
                             appointment(member_id=1), appointment(status=S.CANCELED, member_id=8),
                             appointment(on=datetime(2026, 10, 28), member_id=7)]

        result = overview()

        assert sum(r.income for r in result.members) == pytest.approx(result.business.total_income)
        assert sum(r.booked_revenue for r in result.members) == pytest.approx(result.business.booked_revenue)
        assert sum(r.commission_earned for r in result.members) == pytest.approx(result.business.commission_payable)
        assert sum(r.appointments_made for r in result.members) == result.business.appointments_made


class TestPhotographerView:
    @pytest.fixture(autouse=True)
    def _paula(self, as_member, read):
        as_member(7)
        read.appointments = [appointment(), appointment(member_id=8, price=500.0, commission=100.0)]

    def test_sees_only_their_own_row_without_business_totals(self, overview):
        result = overview()

        assert result.business is None
        assert [r.member_id for r in result.members] == [7]
        assert (result.members[0].income, result.members[0].commission_earned) == (250, 70)
        assert result.comparison is None and result.series is None

    def test_asking_for_their_own_row_is_fine(self, overview):
        assert overview(member_id=7).members[0].member_id == 7

    def test_asking_for_another_members_row_is_refused(self, overview):
        with pytest.raises(UnauthorizedBusinessAction):
            overview(member_id=8)

    def test_asking_for_another_business_is_refused(self, overview):
        with pytest.raises(BusinessError):
            overview(business_id=999)
