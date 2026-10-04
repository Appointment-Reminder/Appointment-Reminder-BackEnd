# tests/domain/overview/test_comparison_and_series.py
from datetime import date, datetime

from tests.domain.overview.conftest import appointment

OCTOBER = (date(2026, 10, 1), date(2026, 10, 30))


class TestComparison:
    def test_the_previous_period_ends_the_day_before_and_has_the_same_length(self, overview):
        c = overview(period=(date(2026, 10, 11), date(2026, 10, 20))).comparison

        assert (c.previous_from, c.previous_to) == (date(2026, 10, 1), date(2026, 10, 10))

    def test_previous_headline_and_percentage_change(self, read, overview):
        read.appointments = [
            appointment(booked=datetime(2026, 9, 5), on=datetime(2026, 9, 12), price=100.0, deposit=0, commission=0),
            appointment(booked=datetime(2026, 10, 5), on=datetime(2026, 10, 12), price=150.0, deposit=0, commission=0),
        ]

        c = overview(period=OCTOBER).comparison

        assert c.previous.total_income == 100
        assert c.previous.appointments_made == 1
        assert c.change_percent.total_income == 50
        assert c.change_percent.booked_revenue == 50
        assert c.change_percent.commission_payable is None  # previous was 0

    def test_a_previous_value_of_zero_gives_no_percentage(self, read, overview):
        read.appointments = [appointment()]

        c = overview().comparison

        assert c.previous.total_income == 0
        assert c.change_percent.total_income is None

    def test_a_drop_is_a_negative_percentage(self, read, overview):
        read.appointments = [
            appointment(booked=datetime(2026, 9, 5), on=datetime(2026, 9, 12), price=200.0, deposit=0),
            appointment(booked=datetime(2026, 10, 5), on=datetime(2026, 10, 12), price=100.0, deposit=0)]

        assert overview(period=OCTOBER).comparison.change_percent.total_income == -50

    def test_owner_take_is_compared_only_for_the_owner(self, read, overview, as_member):
        read.appointments = [appointment(booked=datetime(2026, 9, 5), on=datetime(2026, 9, 12))]
        assert overview(period=OCTOBER).comparison.previous.owner_take == 180

        as_member(2)
        c = overview(period=OCTOBER).comparison
        assert c.previous.owner_take is None and c.change_percent.owner_take is None


class TestSeries:
    def test_no_series_without_group_by(self, overview):
        assert overview().series is None

    def test_day_buckets_include_empty_days_as_zero(self, read, overview):
        read.appointments = [appointment(booked=datetime(2026, 10, 2), on=datetime(2026, 10, 4))]

        series = overview(period=(date(2026, 10, 1), date(2026, 10, 5)), group_by="day").series

        assert [(p.start.day, p.income) for p in series] == [(1, 0), (2, 50), (3, 0), (4, 200), (5, 0)]
        assert series[3].balance_income == 200 and series[1].deposit_income == 50

    def test_week_buckets_start_on_monday(self, read, overview):
        read.appointments = [appointment(booked=datetime(2026, 10, 7), on=datetime(2026, 10, 14))]

        series = overview(period=(date(2026, 10, 1), date(2026, 10, 14)), group_by="week").series

        assert [(p.start, p.income) for p in series] == [
            (date(2026, 9, 28), 0), (date(2026, 10, 5), 50), (date(2026, 10, 12), 200)]

    def test_month_buckets(self, read, overview):
        read.appointments = [appointment(booked=datetime(2026, 9, 20), on=datetime(2026, 10, 5))]

        series = overview(period=(date(2026, 9, 1), date(2026, 10, 14)), group_by="month").series

        assert [(p.start, p.income) for p in series] == [(date(2026, 9, 1), 50), (date(2026, 10, 1), 200)]

    def test_the_series_is_part_of_the_business_view_only(self, overview, as_member):
        as_member(7)

        assert overview(group_by="day").series is None


class TestResponseModel:
    def test_the_overview_serialises_for_every_view(self, read, overview, as_member):
        from app.api.models.overview_model import BusinessOverviewRead
        read.appointments = [appointment()]

        for member_id in (1, 2, 7):
            as_member(member_id)
            BusinessOverviewRead.model_validate(overview(group_by="week")).model_dump(mode="json")
