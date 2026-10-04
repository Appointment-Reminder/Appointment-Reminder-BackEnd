# tests/domain/overview/test_business_kpis.py
"""Business-level KPIs and catalogue breakdowns."""
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus as S
from tests.domain.overview.conftest import appointment, line


class TestAppointmentKpis:
    def test_average_value_excludes_canceled_and_refunded(self, read, overview):
        read.appointments = [appointment(price=200.0), appointment(price=400.0), appointment(status=S.CANCELED)]

        assert overview().business.average_appointment_value == 300

    def test_cancellation_rate_is_canceled_and_refunded_among_those_booked(self, read, overview):
        read.appointments = [appointment(), appointment(), appointment(status=S.CANCELED),
                             appointment(status=S.REFUNDED)]

        assert overview().business.cancellation_rate == 0.5

    def test_referral_sources_are_counted_with_a_bucket_for_none(self, read, overview):
        read.appointments = [appointment(referral_source="Instagram"), appointment(referral_source="Instagram"),
                             appointment(referral_source="Friend"), appointment(),
                             appointment(referral_source="Friend", status=S.CANCELED)]

        sources = overview().business.referral_sources

        assert [(s.source, s.count) for s in sources] == [("Instagram", 2), ("Friend", 1), (None, 1)]

    def test_unresolved_addons_are_counted_for_the_business(self, read, overview):
        read.unresolved = 3

        assert overview().business.unresolved_addons == 3

    def test_an_empty_period_has_no_division_errors(self, overview):
        b = overview().business

        assert (b.average_appointment_value, b.cancellation_rate, b.addon_attach_rate) == (0, 0, 0)
        assert (b.top_addons, b.revenue_by_package, b.revenue_by_category, b.referral_sources) == ([], [], [], [])


class TestCatalogueBreakdowns:
    def test_revenue_by_package_and_category_leave_addons_out(self, read, overview):
        read.appointments = [appointment(price=300.0, package_id=1, addons=[line(1, 50.0)]),
                             appointment(price=100.0, package_id=2),
                             appointment(price=250.0, package_id=1, status=S.CANCELED)]

        b = overview().business

        assert [(l.id, l.name, l.revenue, l.count) for l in b.revenue_by_package] == [
            (1, "Wedding Gold", 250, 1), (2, "Portrait", 100, 1)]
        assert [(l.id, l.name, l.revenue) for l in b.revenue_by_category] == [
            (3, "Wedding", 250), (4, "Family", 100)]

    def test_top_addons_are_ranked_by_revenue(self, read, overview):
        read.appointments = [appointment(price=450.0, addons=[line(1, 30.0), line(2, 120.0, quantity=2)]),
                             appointment(price=280.0, addons=[line(1, 30.0)]),
                             appointment(price=280.0, addons=[line(1, 99.0)], status=S.REFUNDED)]

        top = overview().business.top_addons

        assert [(l.id, l.name, l.revenue, l.count) for l in top] == [(2, "Extra hour", 120, 2), (1, "Album", 60, 2)]

    def test_attach_rate_is_the_share_of_appointments_with_an_addon(self, read, overview):
        read.appointments = [appointment(addons=[line()]), appointment(), appointment(), appointment(),
                             appointment(addons=[line()], status=S.CANCELED)]

        assert overview().business.addon_attach_rate == 0.25
