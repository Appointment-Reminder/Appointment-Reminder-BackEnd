# tests/domain/addon/test_addon_member_read_access.py
"""Every business member can read the active catalogue; changing it stays owner/admin."""
import pytest
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.models.addon import Addon
from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.models.business_member_model import MemberRole


def _addon(**overrides):
    values = dict(id=1, business_id=100, name="Extra photos", jotform_alias="10 extra photos", is_active=True)
    values.update(overrides)
    return Addon(**values)


@pytest.fixture
def as_role(business_guard):
    def _as(role):
        business_guard.ensure_is_a_member.return_value = Mock(id=5, role=role)
    return _as


class TestListAddons:
    @pytest.mark.parametrize("role", [MemberRole.PHOTOGRAPHER, MemberRole.ASSISTANT])
    def test_a_regular_member_lists_only_active_addons(self, service, addon_repo, as_role, role, user):
        as_role(role)
        addon_repo.list_by_business.side_effect = lambda business_id, is_active=None: [
            a for a in [_addon(id=1), _addon(id=2, is_active=False, jotform_alias="b")]
            if is_active is None or a.is_active == is_active]

        result = service.list(100, user)

        assert [a.id for a in result] == [1]

    @pytest.mark.parametrize("role", [MemberRole.OWNER, MemberRole.ADMIN])
    def test_owner_and_admin_still_list_inactive_addons_too(self, service, addon_repo, as_role, role, user):
        as_role(role)
        addon_repo.list_by_business.side_effect = lambda business_id, is_active=None: [
            a for a in [_addon(id=1), _addon(id=2, is_active=False, jotform_alias="b")]
            if is_active is None or a.is_active == is_active]

        assert [a.id for a in service.list(100, user)] == [1, 2]

    def test_someone_outside_the_business_is_rejected(self, service, business_guard, addon_repo, user):
        business_guard.ensure_is_a_member.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.list(100, user)
        addon_repo.list_by_business.assert_not_called()


class TestGetAddon:
    def test_a_regular_member_reads_an_active_addon(self, service, addon_repo, as_role, user):
        as_role(MemberRole.PHOTOGRAPHER)
        addon_repo.get_by_id.return_value = _addon(id=1)

        assert service.get(1, user).id == 1

    def test_a_regular_member_cannot_read_an_inactive_addon(self, service, addon_repo, as_role, user):
        as_role(MemberRole.ASSISTANT)
        addon_repo.get_by_id.return_value = _addon(id=1, is_active=False)

        with pytest.raises(AddonError):
            service.get(1, user)

    def test_admin_reads_an_inactive_addon(self, service, addon_repo, as_role, user):
        as_role(MemberRole.ADMIN)
        addon_repo.get_by_id.return_value = _addon(id=1, is_active=False)

        assert service.get(1, user).is_active is False

    def test_member_of_another_business_is_rejected(self, service, business_guard, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1, business_id=555)
        business_guard.ensure_is_a_member.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.get(1, user)
        business_guard.ensure_is_a_member.assert_called_with(555, 9)


class TestChangesStayAdminOnly:
    @pytest.fixture(autouse=True)
    def _not_admin(self, business_guard, addon_repo):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()
        addon_repo.get_by_id.return_value = _addon(id=1)

    def test_create_update_and_deactivate_are_rejected(self, service, addon_repo, user):
        with pytest.raises(BusinessError):
            service.create(_addon(id=None), user)
        with pytest.raises(BusinessError):
            service.update(_addon(id=1), user)
        with pytest.raises(BusinessError):
            service.deactivate(1, user)
        addon_repo.create.assert_not_called()
        addon_repo.update.assert_not_called()

    def test_price_history_and_current_price_are_rejected(self, service, price_repo, user):
        with pytest.raises(BusinessError):
            service.get_price_history(1, user)
        with pytest.raises(BusinessError):
            service.get_current_price(1, user)
        price_repo.get_history.assert_not_called()
