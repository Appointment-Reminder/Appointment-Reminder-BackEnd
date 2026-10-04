# tests/domain/addon/test_addon_booking_resolution.py
"""Seam 1: booking resolution of Jotform add-on labels into Appointment Add-ons and Unresolved Add-ons."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.domain.Jotform.service.jotform_submission_assembler import resolve_booking_context
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.addon.models.addon_price import AddonPrice
from app.domain.addon.service.addon_booking import AddonBookingResolver
from app.domain.Jotform.models.jotform_form_model import JotformFormAssignment
from app.domain.business.models.member_commission import MemberCommission
from app.domain.package.models.package import Package
from app.domain.package.models.package_price import PackagePrice

NOW = datetime(2026, 10, 4, 12, 0)


class Catalogue:
    """In-memory stand-in behind the mocked add-on ports."""

    def __init__(self):
        self.addons: list[Addon] = []
        self.prices: dict[int, list[AddonPrice]] = {}
        self.commissions: dict[tuple[int, int], list[AddonCommission]] = {}

    def add(self, id, alias, price=50, price_days=-10, **kw):
        values = dict(business_id=100, name=alias, jotform_alias=alias, is_active=True)
        values.update(kw)
        self.addons.append(Addon(id=id, **values))
        if price is not None:
            self.prices[id] = [AddonPrice(id=id * 10, addon_id=id, price=price,
                                          effective_from=NOW + timedelta(days=price_days))]
        return self

    def commission(self, member_id, addon_id, amount, pct):
        self.commissions.setdefault((member_id, addon_id), []).append(AddonCommission(
            business_member_id=member_id, addon_id=addon_id, commission_amount=amount,
            commission_isPercentage=pct, effective_from=NOW - timedelta(days=1)))
        return self

    def resolver(self) -> AddonBookingResolver:
        addon_repo, price_repo, commission_repo = Mock(), Mock(), Mock()
        addon_repo.find_by_alias.side_effect = lambda business_id, alias: [
            a for a in self.addons if a.business_id == business_id and a.jotform_alias == alias]
        price_repo.get_history.side_effect = lambda addon_id: list(self.prices.get(addon_id, []))
        commission_repo.get_history.side_effect = lambda member_id, addon_id: list(
            self.commissions.get((member_id, addon_id), []))
        return AddonBookingResolver(addon_repo=addon_repo, price_repo=price_repo, commission_repo=commission_repo)


@pytest.fixture
def catalogue():
    return Catalogue()


@pytest.fixture
def package_guard():
    guard = Mock()
    guard.resolve_package_by_submission_alias.return_value = Package(
        id=1, business_id=100, category_id=2, name="Gold", description="d", is_active=True,
        jotform_alias="Gold Package", package_duration=60)
    return guard


@pytest.fixture
def jotform_guard():
    guard = Mock()
    guard.resolve_assignment_or_unknown.return_value = JotformFormAssignment(
        id=1, form_id=10, business_member_id=7, category_id=2)
    return guard


@pytest.fixture
def member_repo():
    repo = Mock()
    repo.get_current_commission.return_value = MemberCommission(
        id=1, business_member_id=7, package_id=1, commission_amount=10, commission_isPercentage=True,
        effective_from=NOW)
    return repo


@pytest.fixture
def price_repo():
    repo = Mock()
    repo.get_current_price.return_value = PackagePrice(
        id=1, package_id=1, total_price=500, deposit_amount=100, remaining_amount=400, effective_from=NOW)
    return repo


@pytest.fixture
def book(package_guard, jotform_guard, member_repo, price_repo, catalogue):
    def _book(labels, resolver=None):
        return resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
            addon_labels=labels, addon_resolver=resolver or catalogue.resolver(), now=NOW,
        )
    return _book


class TestMatchedAddons:
    def test_two_matched_addons_become_two_appointment_addons_with_frozen_values(self, book, catalogue):
        catalogue.add(1, "10 extra photos", price=50).commission(7, 1, 10, pct=True)
        catalogue.add(2, "Prints", price=30).commission(7, 2, 4, pct=False)

        result = book(["10 extra photos", "Prints"])

        first, second = result.addons
        assert (first.addon_id, first.addon_price_id, first.quantity) == (1, 10, 1)
        assert (first.unit_price, first.price_total) == (50.0, 50.0)
        assert (first.unit_commission_percent, first.commission_total) == (10.0, 5.0)
        assert (second.addon_id, second.quantity, second.unit_price) == (2, 1, 30.0)
        assert (second.unit_commission_amount, second.commission_total) == (4.0, 4.0)
        assert result.unresolved_addon_labels == []

    def test_totals_include_addons_and_the_deposit_is_unchanged(self, book, catalogue):
        catalogue.add(1, "A", price=50).commission(7, 1, 10, pct=True)
        catalogue.add(2, "B", price=30).commission(7, 2, 4, pct=False)

        result = book(["A", "B"])

        assert result.price_at_booking == 580.0          # 500 + 50 + 30
        assert result.remaining_amount == 480.0          # 400 + 50 + 30
        assert result.deposit_amount == 100.0
        assert result.commission_amount_at_booking == 59.0   # 50 package + 5 + 4
        assert result.fully_resolved is True

    def test_duration_is_added_only_for_addons_with_duration(self, book, catalogue):
        catalogue.add(1, "Extra hour", has_duration=True, duration_minutes=30)
        catalogue.add(2, "Prints")

        result = book(["Extra hour", "Prints"])

        assert result.appointment_duration == 90          # 60 package + 30
        assert result.addons[1].unit_duration == 0

    def test_member_without_commission_row_earns_zero_on_the_addon(self, book, catalogue):
        catalogue.add(1, "A", price=50)

        line = book(["A"]).addons[0]

        assert (line.unit_commission_amount, line.unit_commission_percent, line.commission_total) == (0.0, None, 0.0)

    def test_without_an_assigned_member_nothing_is_priced_so_every_label_stays_unresolved(
        self, book, catalogue, jotform_guard
    ):
        jotform_guard.resolve_assignment_or_unknown.return_value = None
        catalogue.add(1, "A", price=50)

        result = book(["A"])

        assert result.addons == []
        assert result.unresolved_addon_labels == ["A"]
        assert result.fully_resolved is False
        assert result.price_at_booking is None

    def test_a_package_without_a_price_keeps_every_label_unresolved(self, book, catalogue, price_repo):
        price_repo.get_current_price.return_value = None
        catalogue.add(1, "A", price=50)

        result = book(["A", "B", "A"])

        assert result.addons == []
        assert result.unresolved_addon_labels == ["A", "B"]

    def test_a_catalogue_price_change_after_booking_does_not_alter_the_booked_line(self, book, catalogue):
        catalogue.add(1, "A", price=50)
        line = book(["A"]).addons[0]

        catalogue.prices[1].append(AddonPrice(id=99, addon_id=1, price=500, effective_from=NOW - timedelta(days=1)))

        assert (line.unit_price, line.price_total, line.addon_price_id) == (50.0, 50.0, 10)

    def test_the_same_addon_chosen_twice_is_booked_once(self, book, catalogue):
        catalogue.add(1, "A", price=50)

        result = book(["A", "A", "  A "])

        assert len(result.addons) == 1
        assert result.price_at_booking == 550.0

    def test_addon_with_a_price_in_effect_later_than_now_is_not_booked_here(self, book, catalogue):
        catalogue.add(1, "A", price=50, price_days=+3)

        assert book(["A"]).addons == []

    def test_non_breaking_spaces_in_the_label_still_match(self, book, catalogue):
        catalogue.add(1, "10 extra photos", price=50)

        assert len(book(["10 extra photos"]).addons) == 1


class TestNoAddons:
    def test_submission_without_addon_labels_behaves_as_before(self, book):
        result = book([])

        assert result.addons == [] and result.unresolved_addon_labels == []
        assert (result.price_at_booking, result.remaining_amount, result.commission_amount_at_booking) == (500.0, 400.0, 50.0)
        assert result.appointment_duration == 60

    def test_none_labels_behave_as_no_labels(self, book):
        assert book(None).addons == []

    def test_a_single_string_label_is_one_label(self, book, catalogue):
        catalogue.add(1, "A", price=50)

        assert len(book("A").addons) == 1

    def test_no_resolver_means_no_addon_work(self, package_guard, jotform_guard, member_repo, price_repo):
        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )
        assert result.addons == [] and result.price_at_booking == 500.0


class TestUnresolvedAddons:
    def test_unknown_label_is_kept_as_unresolved_and_the_package_is_still_booked(self, book, catalogue):
        result = book(["Mystery extra"])

        assert result.unresolved_addon_labels == ["Mystery extra"]
        assert result.addons == []
        assert result.fully_resolved is True
        assert result.price_at_booking == 500.0

    def test_ambiguous_alias_is_unresolved(self, book, catalogue):
        catalogue.add(1, "Album", price=50).add(2, "Album", price=80)

        result = book(["Album"])

        assert result.unresolved_addon_labels == ["Album"]
        assert result.addons == []

    def test_label_matching_only_an_inactive_addon_is_unresolved(self, book, catalogue):
        catalogue.add(1, "Retired extra", price=50, is_active=False)

        result = book(["Retired extra"])

        assert result.unresolved_addon_labels == ["Retired extra"]

    def test_an_active_addon_wins_over_an_inactive_one_with_the_same_alias(self, book, catalogue):
        catalogue.add(1, "Album", price=50, is_active=False).add(2, "Album", price=80)

        result = book(["Album"])

        assert [l.addon_id for l in result.addons] == [2]
        assert result.unresolved_addon_labels == []

    def test_addon_with_no_price_in_effect_is_unresolved(self, book, catalogue):
        catalogue.add(1, "Unpriced", price=None)

        assert book(["Unpriced"]).unresolved_addon_labels == ["Unpriced"]

    def test_addon_with_only_a_future_price_is_unresolved(self, book, catalogue):
        catalogue.add(1, "Soon", price=50, price_days=+3)

        result = book(["Soon"])

        assert result.unresolved_addon_labels == ["Soon"]
        assert result.addons == []

    def test_addon_restricted_to_another_package_category_is_unresolved(self, book, catalogue):
        catalogue.add(1, "Wedding album", price=50, category_id=99)

        assert book(["Wedding album"]).unresolved_addon_labels == ["Wedding album"]

    def test_addon_restricted_to_the_package_category_is_booked(self, book, catalogue):
        catalogue.add(1, "Gold album", price=50, category_id=2)

        assert len(book(["Gold album"]).addons) == 1

    def test_matched_labels_in_the_same_submission_are_still_booked(self, book, catalogue):
        catalogue.add(1, "A", price=50)

        result = book(["A", "Mystery", "Unpriced"])

        assert [l.addon_id for l in result.addons] == [1]
        assert result.unresolved_addon_labels == ["Mystery", "Unpriced"]
        assert result.price_at_booking == 550.0

    def test_unresolved_labels_never_turn_a_resolved_booking_into_needs_assignment(self, book, catalogue):
        assert book(["Mystery"]).fully_resolved is True

    def test_unresolved_labels_are_kept_even_when_the_package_is_unresolved(self, book, catalogue, package_guard):
        package_guard.resolve_package_by_submission_alias.return_value = None

        result = book(["Mystery"])

        assert result.fully_resolved is False
        assert result.unresolved_addon_labels == ["Mystery"]

    def test_the_raw_label_is_kept_as_submitted_apart_from_surrounding_whitespace(self, book, catalogue):
        assert book(["  Mystery extra "]).unresolved_addon_labels == ["Mystery extra"]

    def test_the_same_unknown_label_twice_is_kept_once(self, book, catalogue):
        assert book(["Mystery", "Mystery"]).unresolved_addon_labels == ["Mystery"]
