# tests/domain/addon/test_member_addon_commissions.py
"""One call lists the commission a member has in effect on every active Add-on of the business."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.business.errors.business_errors import BusinessError


def _addon(id, **overrides):
    values = dict(business_id=100, name=f"addon {id}", jotform_alias=f"alias {id}", is_active=True)
    values.update(overrides)
    return Addon(id=id, **values)


def _commission(id, addon_id, amount, pct, days, member_id=7):
    return AddonCommission(
        id=id, business_member_id=member_id, addon_id=addon_id, commission_amount=amount,
        commission_isPercentage=pct, effective_from=datetime.now() + timedelta(days=days))


@pytest.fixture(autouse=True)
def _member_of_the_business(business_guard):
    business_guard.ensure_member_exist.return_value = Mock(id=7, business_id=100)


@pytest.fixture
def histories(commission_repo):
    """The member's commission history per add-on id, served the way the batch lookup does."""
    stored = {}
    commission_repo.get_histories_for_member.side_effect = lambda member_id: stored
    return stored


class TestListMemberAddonCommissions:
    def test_lists_the_commission_in_effect_for_each_active_addon(self, service, addon_repo, histories, user):
        addon_repo.list_by_business.return_value = [_addon(1), _addon(2)]
        histories[1] = [_commission(10, 1, 10, True, -30), _commission(11, 1, 15, True, -1), _commission(12, 1, 50, True, +5)]
        histories[2] = [_commission(20, 2, 8, False, -2)]

        result = service.list_member_addon_commissions(100, 7, user)

        assert [(c.id, c.addon_id, c.commission_amount, c.commission_isPercentage) for c in result] == [
            (11, 1, 15, True), (20, 2, 8, False)]

    def test_an_addon_without_a_row_gets_a_flat_zero_and_no_id(self, service, addon_repo, histories, user):
        addon_repo.list_by_business.return_value = [_addon(1), _addon(2)]
        histories[1] = [_commission(10, 1, 10, True, -1)]

        result = service.list_member_addon_commissions(100, 7, user)

        default = result[1]
        assert (default.id, default.business_member_id, default.addon_id) == (None, 7, 2)
        assert (default.commission_amount, default.commission_isPercentage) == (0, False)

    def test_an_addon_with_only_a_future_row_gets_the_zero_default(self, service, addon_repo, histories, user):
        addon_repo.list_by_business.return_value = [_addon(1)]
        histories[1] = [_commission(10, 1, 40, True, +3)]

        assert service.list_member_addon_commissions(100, 7, user)[0].commission_amount == 0

    def test_only_active_addons_are_listed(self, service, addon_repo, histories, user):
        addon_repo.list_by_business.return_value = []

        service.list_member_addon_commissions(100, 7, user)

        addon_repo.list_by_business.assert_called_once_with(100, is_active=True)

    def test_history_is_read_once_for_the_member(self, service, addon_repo, commission_repo, histories, user):
        addon_repo.list_by_business.return_value = [_addon(1), _addon(2), _addon(3)]

        service.list_member_addon_commissions(100, 7, user)

        commission_repo.get_histories_for_member.assert_called_once_with(7)
        commission_repo.get_history.assert_not_called()

    def test_a_member_of_another_business_is_rejected(self, service, business_guard, commission_repo, user):
        business_guard.ensure_member_exist.return_value = Mock(id=7, business_id=555)

        with pytest.raises(AddonError):
            service.list_member_addon_commissions(100, 7, user)
        commission_repo.get_histories_for_member.assert_not_called()

    def test_only_owner_and_admin_can_list(self, service, business_guard, commission_repo, user):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.list_member_addon_commissions(100, 7, user)
        business_guard.ensure_admin_or_owner.assert_called_with(100, 9)
        commission_repo.get_histories_for_member.assert_not_called()
