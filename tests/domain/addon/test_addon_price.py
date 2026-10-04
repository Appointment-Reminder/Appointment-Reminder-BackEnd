# tests/domain/addon/test_addon_price.py
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError, NoAddonPriceInEffect
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_price import AddonPrice, price_in_effect
from app.domain.business.errors.business_errors import BusinessError

NOW = datetime(2026, 10, 4, 12, 0)


def _price(id=1, price=50, days=0, addon_id=1):
    return AddonPrice(id=id, addon_id=addon_id, price=price, effective_from=NOW + timedelta(days=days))


class TestPriceInEffect:
    def test_latest_price_whose_date_has_passed_wins(self):
        prices = [_price(1, 40, days=-30), _price(2, 50, days=-10), _price(3, 60, days=-1)]
        assert price_in_effect(prices, NOW).id == 3

    def test_input_order_does_not_matter(self):
        prices = [_price(3, 60, days=-1), _price(1, 40, days=-30), _price(2, 50, days=-10)]
        assert price_in_effect(prices, NOW).id == 3

    def test_future_dated_price_is_not_in_effect_until_its_date(self):
        prices = [_price(1, 40, days=-30), _price(2, 99, days=+5)]
        assert price_in_effect(prices, NOW).id == 1
        assert price_in_effect(prices, NOW + timedelta(days=5)).id == 2

    def test_price_taking_effect_exactly_now_is_in_effect(self):
        assert price_in_effect([_price(1, 40, days=0)], NOW).id == 1

    def test_no_price_at_all_is_none(self):
        assert price_in_effect([], NOW) is None

    def test_only_future_dated_prices_is_none(self):
        assert price_in_effect([_price(1, 40, days=+1)], NOW) is None


class TestAddonPriceService:
    @pytest.fixture(autouse=True)
    def _addon_of_business_100(self, addon_repo):
        addon_repo.get_by_id.return_value = Addon(id=1, business_id=100, name="x", jotform_alias="x")

    def test_owner_can_add_a_price_with_an_effective_date(self, service, price_repo, user):
        created = service.create_price(AddonPrice(addon_id=1, price=50, effective_from=NOW), user)

        assert created.price == 50
        assert created.effective_from == NOW
        price_repo.create.assert_called_once()

    def test_price_of_an_addon_of_another_business_is_rejected(self, service, business_guard, price_repo, user):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.create_price(AddonPrice(addon_id=1, price=50, effective_from=NOW), user)
        price_repo.create.assert_not_called()

    def test_negative_price_is_rejected(self, service, price_repo, user):
        with pytest.raises(AddonError):
            service.create_price(AddonPrice(addon_id=1, price=-1, effective_from=NOW), user)
        price_repo.create.assert_not_called()

    def test_current_price_is_the_one_in_effect(self, service, price_repo, user):
        price_repo.get_history.return_value = [
            _price(1, 40, days=-30), _price(2, 50, days=-1), _price(3, 99, days=+30),
        ]

        assert service.get_current_price(1, user, at=NOW).price == 50

    def test_no_price_in_effect_is_reported_explicitly(self, service, price_repo, user):
        price_repo.get_history.return_value = [_price(1, 99, days=+30)]

        with pytest.raises(NoAddonPriceInEffect):
            service.get_current_price(1, user, at=NOW)

    def test_addon_without_any_price_reports_no_price_in_effect(self, service, price_repo, user):
        price_repo.get_history.return_value = []

        with pytest.raises(NoAddonPriceInEffect):
            service.get_current_price(1, user, at=NOW)

    def test_past_prices_are_kept_as_history(self, service, price_repo, user):
        history = [_price(1, 40, days=-30), _price(2, 50, days=-1)]
        price_repo.get_history.return_value = history

        assert service.get_price_history(1, user) == history
