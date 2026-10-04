# tests/domain/addon/test_addon_current_price.py
"""Add-on responses carry the price in effect now, so a list needs no per-add-on price lookup."""
import pytest
from datetime import datetime, timedelta

from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_price import AddonPrice


def _addon(**overrides):
    values = dict(id=1, business_id=100, name="Extra photos", jotform_alias="10 extra photos")
    values.update(overrides)
    return Addon(**values)


def _price(addon_id, price, days):
    return AddonPrice(addon_id=addon_id, price=price, effective_from=datetime.now() + timedelta(days=days))


@pytest.fixture
def prices(price_repo):
    """Price history per add-on id, served the way the batch lookup does."""
    histories = {}
    price_repo.get_histories.side_effect = lambda ids: {i: histories[i] for i in ids if i in histories}
    return histories


class TestCurrentPriceOnAddons:
    def test_list_shows_the_price_in_effect_for_each_addon(self, service, addon_repo, prices, user):
        addon_repo.list_by_business.return_value = [_addon(id=1), _addon(id=2, jotform_alias="b")]
        prices[1] = [_price(1, 20, -30), _price(1, 25, -1), _price(1, 40, +5)]
        prices[2] = [_price(2, 60, -2)]

        result = service.list(100, user)

        assert [(a.id, a.current_price) for a in result] == [(1, 25), (2, 60)]

    def test_addon_without_a_price_has_no_current_price(self, service, addon_repo, prices, user):
        addon_repo.list_by_business.return_value = [_addon(id=1)]

        assert service.list(100, user)[0].current_price is None

    def test_addon_with_only_a_future_price_has_no_current_price(self, service, addon_repo, prices, user):
        addon_repo.list_by_business.return_value = [_addon(id=1)]
        prices[1] = [_price(1, 40, +5)]

        assert service.list(100, user)[0].current_price is None

    def test_list_looks_prices_up_once_for_all_addons(self, service, addon_repo, price_repo, prices, user):
        addon_repo.list_by_business.return_value = [_addon(id=1), _addon(id=2, jotform_alias="b")]

        service.list(100, user)

        price_repo.get_histories.assert_called_once_with([1, 2])
        price_repo.get_history.assert_not_called()

    def test_get_shows_the_current_price(self, service, addon_repo, prices, user):
        addon_repo.get_by_id.return_value = _addon(id=1)
        prices[1] = [_price(1, 25, -1)]

        assert service.get(1, user).current_price == 25

    def test_create_update_and_deactivate_show_the_current_price(self, service, addon_repo, prices, user):
        addon_repo.get_by_id.return_value = _addon(id=1)
        prices[1] = [_price(1, 25, -1)]

        assert service.create(_addon(id=None), user).current_price == 25
        assert service.update(_addon(id=1), user).current_price == 25
        assert service.deactivate(1, user).current_price == 25
