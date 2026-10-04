# tests/domain/addon/test_addon_commission.py
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission, commission_in_effect
from app.domain.business.errors.business_errors import BusinessError

NOW = datetime(2026, 10, 4, 12, 0)


def _commission(id=1, amount=10, pct=True, days=0, member_id=7, addon_id=1):
    return AddonCommission(
        id=id, business_member_id=member_id, addon_id=addon_id,
        commission_amount=amount, commission_isPercentage=pct, effective_from=NOW + timedelta(days=days),
    )


class TestCommissionInEffect:
    def test_latest_commission_whose_date_has_passed_wins(self):
        history = [_commission(1, 10, days=-30), _commission(2, 20, days=-1), _commission(3, 30, days=+5)]
        assert commission_in_effect(history, member_id=7, addon_id=1, at=NOW).id == 2

    def test_percentage_and_flat_are_both_supported(self):
        flat = commission_in_effect([_commission(1, 15, pct=False, days=-1)], 7, 1, NOW)
        pct = commission_in_effect([_commission(2, 15, pct=True, days=-1)], 7, 1, NOW)
        assert (flat.commission_isPercentage, pct.commission_isPercentage) == (False, True)

    def test_missing_row_yields_a_zero_commission(self):
        result = commission_in_effect([], member_id=7, addon_id=1, at=NOW)

        assert result.commission_amount == 0
        assert result.commission_isPercentage is False

    def test_only_future_dated_rows_yield_a_zero_commission(self):
        result = commission_in_effect([_commission(1, 40, days=+3)], member_id=7, addon_id=1, at=NOW)
        assert result.commission_amount == 0


class TestAddonCommissionService:
    @pytest.fixture(autouse=True)
    def _setup(self, addon_repo, business_guard):
        addon_repo.get_by_id.return_value = Addon(id=1, business_id=100, name="x", jotform_alias="x")
        business_guard.ensure_member_exist.return_value = Mock(id=7, business_id=100, user_id=70)

    def test_owner_sets_a_percentage_commission(self, service, commission_repo, user):
        created = service.create_commission(_commission(id=None, amount=15, pct=True), user)

        assert (created.commission_amount, created.commission_isPercentage) == (15, True)
        commission_repo.create.assert_called_once()

    def test_owner_sets_a_flat_commission(self, service, user):
        created = service.create_commission(_commission(id=None, amount=5, pct=False), user)
        assert (created.commission_amount, created.commission_isPercentage) == (5, False)

    def test_member_of_another_business_is_rejected(self, service, business_guard, commission_repo, user):
        business_guard.ensure_member_exist.return_value = Mock(id=7, business_id=555, user_id=70)

        with pytest.raises(AddonError):
            service.create_commission(_commission(id=None), user)
        commission_repo.create.assert_not_called()

    def test_addon_of_another_business_is_rejected(self, service, business_guard, commission_repo, user):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.create_commission(_commission(id=None), user)
        commission_repo.create.assert_not_called()

    @pytest.mark.parametrize("amount,pct", [(-1, False), (-1, True), (101, True)])
    def test_out_of_range_amount_is_rejected(self, service, commission_repo, user, amount, pct):
        with pytest.raises(AddonError):
            service.create_commission(_commission(id=None, amount=amount, pct=pct), user)
        commission_repo.create.assert_not_called()

    def test_current_commission_reads_the_row_in_effect(self, service, commission_repo, user):
        commission_repo.get_history.return_value = [_commission(1, 10, days=-30), _commission(2, 25, days=-1)]

        assert service.get_current_commission(7, 1, user, at=NOW).commission_amount == 25

    def test_current_commission_is_zero_when_no_row(self, service, commission_repo, user):
        commission_repo.get_history.return_value = []

        assert service.get_current_commission(7, 1, user, at=NOW).commission_amount == 0
