# tests/domain/addon/test_addon_commission_correction.py
"""A Commission Correction fixes a version in place; the version's member, add-on and date never move."""
import pytest
from datetime import datetime

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.business.errors.business_errors import BusinessError

STARTED = datetime(2026, 9, 1)


def _stored(id=5, amount=10, pct=True):
    return AddonCommission(id=id, business_member_id=7, addon_id=1, commission_amount=amount,
                           commission_isPercentage=pct, effective_from=STARTED)


def _correct(service, user, id=5, amount=15, pct=False):
    return service.correct_commission(id, amount, pct, user)


@pytest.fixture(autouse=True)
def _stored_commission(commission_repo, addon_repo):
    commission_repo.get_by_id.side_effect = lambda commission_id: _stored() if commission_id == 5 else None
    commission_repo.update.side_effect = lambda c: c
    addon_repo.get_by_id.return_value = Addon(id=1, business_id=100, name="x", jotform_alias="x")


class TestCorrectCommission:
    def test_fixes_the_amount_and_kind_in_place(self, service, commission_repo, user):
        corrected = _correct(service, user, amount=15, pct=False)

        assert (corrected.id, corrected.commission_amount, corrected.commission_isPercentage) == (5, 15, False)
        commission_repo.update.assert_called_once()
        commission_repo.create.assert_not_called()

    def test_member_addon_and_effective_date_are_kept(self, service, user):
        corrected = _correct(service, user)

        assert (corrected.business_member_id, corrected.addon_id, corrected.effective_from) == (7, 1, STARTED)

    def test_unknown_commission_is_rejected(self, service, commission_repo, user):
        with pytest.raises(AddonError):
            _correct(service, user, id=999)
        commission_repo.update.assert_not_called()

    def test_non_admin_of_the_addons_business_is_rejected(self, service, business_guard, commission_repo, user):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            _correct(service, user)
        business_guard.ensure_admin_or_owner.assert_called_with(100, 9)
        commission_repo.update.assert_not_called()

    @pytest.mark.parametrize("amount,pct", [(-1, False), (-1, True), (101, True)])
    def test_invalid_amounts_are_rejected(self, service, commission_repo, user, amount, pct):
        with pytest.raises(AddonError):
            _correct(service, user, amount=amount, pct=pct)
        commission_repo.update.assert_not_called()

    def test_a_flat_amount_above_100_is_allowed(self, service, user):
        assert _correct(service, user, amount=150, pct=False).commission_amount == 150
