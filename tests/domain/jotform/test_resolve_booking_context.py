# tests/domain/jotform/test_resolve_booking_context.py
import pytest
from datetime import datetime
from unittest.mock import Mock

from app.domain.Jotform.service.jotform_submission_assembler import resolve_booking_context
from app.domain.package.models.package import Package
from app.domain.package.models.package_price import PackagePrice
from app.domain.Jotform.models.jotform_form_model import JotformFormAssignment
from app.domain.business.models.member_commission import MemberCommission


@pytest.fixture
def package_guard():
    return Mock()

@pytest.fixture
def jotform_guard():
    return Mock()

@pytest.fixture
def member_repo():
    return Mock()

@pytest.fixture
def price_repo():
    return Mock()


def _package(id=1, category_id=2):
    return Package(id=id, business_id=100, category_id=category_id, name="Gold", description="d", is_active=True, jotform_alias="Gold Package")

def _assignment(member_id=7):
    return JotformFormAssignment(id=1, form_id=10, business_member_id=member_id, category_id=2)

def _price(package_id=1, total=500, deposit=100, remaining=400, personal=False):
    return PackagePrice(id=1, package_id=package_id, total_price=total, deposit_amount=deposit, remaining_amount=remaining, effective_from=datetime.now())

def _commission(amount=10, is_pct=True):
    return MemberCommission(id=1, business_member_id=7, package_id=1, commission_amount=amount, commission_isPercentage=is_pct, effective_from=datetime.now())


class TestResolveBookingContext:
    def test_fully_resolved_happy_path(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = _assignment()
        price_repo.get_current_price.return_value = _price()
        member_repo.get_current_commission.return_value = _commission(amount=10, is_pct=True)

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.fully_resolved is True
        assert result.package_id == 1
        assert result.member_id == 7
        assert result.price_at_booking == 500.0
        assert result.deposit_amount == 100.0
        assert result.remaining_amount == 400.0
        assert result.commission_percent_at_booking == 10.0
        assert result.commission_amount_at_booking == 50.0  # 500 * 10%

    def test_package_unresolved(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = None

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Unknown Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.fully_resolved is False
        assert result.package_id is None
        assert result.member_id is None
        assert result.price_at_booking is None
        jotform_guard.resolve_assignment_or_unknown.assert_not_called()

    def test_assignment_unresolved(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = None

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.fully_resolved is False
        assert result.package_id == 1     # package still recorded
        assert result.member_id is None
        assert result.price_at_booking is None
        price_repo.get_current_price.assert_not_called()

    def test_no_current_price_configured(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = _assignment()
        price_repo.get_current_price.return_value = None

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.fully_resolved is False
        assert result.member_id == 7
        assert result.package_price_id is None

    def test_no_commission_row_still_fully_resolved_zero_amount(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = _assignment()
        price_repo.get_current_price.return_value = _price()
        member_repo.get_current_commission.return_value = None

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.fully_resolved is True
        assert result.commission_amount_at_booking == 0.0
        assert result.commission_percent_at_booking is None

    def test_commission_percentage_computed_correctly(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = _assignment()
        price_repo.get_current_price.return_value = _price(total=1000)
        member_repo.get_current_commission.return_value = _commission(amount=15, is_pct=True)

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.commission_amount_at_booking == 150.0  # 1000 * 15%
        assert result.commission_percent_at_booking == 15.0

    def test_commission_flat_amount_used_directly(self, package_guard, jotform_guard, member_repo, price_repo):
        package_guard.resolve_package_by_submission_alias.return_value = _package()
        jotform_guard.resolve_assignment_or_unknown.return_value = _assignment()
        price_repo.get_current_price.return_value = _price(total=1000)
        member_repo.get_current_commission.return_value = _commission(amount=75, is_pct=False)

        result = resolve_booking_context(
            business_id=100, form_id=10, package_alias_raw="Gold Package",
            package_guard=package_guard, jotform_guard=jotform_guard,
            member_repo=member_repo, price_repo=price_repo,
        )

        assert result.commission_amount_at_booking == 75.0
        assert result.commission_percent_at_booking is None

