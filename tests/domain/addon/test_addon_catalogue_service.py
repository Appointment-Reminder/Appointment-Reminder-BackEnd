# tests/domain/addon/test_addon_catalogue_service.py
import pytest
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon import Addon
from app.domain.addon.service.addon_service import AddonService
from app.domain.business.errors.business_errors import BusinessError
from app.domain.package.models.package_category_model import PackageCategory


def _addon(**overrides):
    values = dict(
        id=None, business_id=100, name="Extra photos", jotform_alias="10 extra photos",
        is_active=True, category_id=None, has_duration=False, has_quantity=False, duration_minutes=None,
    )
    values.update(overrides)
    return Addon(**values)


class TestCreateAddon:
    def test_creates_active_addon_with_normalized_alias(self, service, addon_repo, user):
        created = service.create(_addon(jotform_alias="  10 extra photos "), user)

        assert created.id == 1
        assert created.is_active is True
        assert created.jotform_alias == "10 extra photos"

    def test_non_admin_cannot_create(self, service, business_guard, addon_repo, user):
        business_guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.create(_addon(), user)
        addon_repo.create.assert_not_called()

    def test_has_duration_without_duration_is_rejected(self, service, addon_repo, user):
        with pytest.raises(AddonError):
            service.create(_addon(has_duration=True, duration_minutes=None), user)
        with pytest.raises(AddonError):
            service.create(_addon(has_duration=True, duration_minutes=0), user)
        addon_repo.create.assert_not_called()

    def test_duration_is_kept_when_has_duration(self, service, user):
        created = service.create(_addon(has_duration=True, duration_minutes=30), user)
        assert created.duration_minutes == 30

    def test_duration_is_dropped_when_no_duration_flag(self, service, user):
        created = service.create(_addon(has_duration=False, duration_minutes=30), user)
        assert created.duration_minutes is None

    def test_duplicate_alias_in_same_business_is_rejected(self, service, addon_repo, user):
        addon_repo.find_by_alias.return_value = [_addon(id=2)]

        with pytest.raises(AddonError):
            service.create(_addon(), user)
        addon_repo.find_by_alias.assert_called_with(100, "10 extra photos")
        addon_repo.create.assert_not_called()

    def test_blank_alias_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.create(_addon(jotform_alias="   "), user)

    def test_category_from_another_business_is_rejected(self, service, package_guard, user):
        package_guard.ensure_category_exist.return_value = PackageCategory(id=3, business_id=555, name="Other")

        with pytest.raises(AddonError):
            service.create(_addon(category_id=3), user)

    def test_category_is_optional(self, service, package_guard, user):
        service.create(_addon(category_id=None), user)
        package_guard.ensure_category_exist.assert_not_called()


class TestReadAddons:
    def test_list_requires_membership_of_that_business(self, service, business_guard, addon_repo, user):
        addon_repo.list_by_business.return_value = [_addon(id=1)]

        assert service.list(100, user) == [_addon(id=1)]
        business_guard.ensure_is_a_member.assert_called_with(100, 9)

    def test_addon_of_another_business_is_not_visible(self, service, business_guard, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1, business_id=555)
        business_guard.ensure_is_a_member.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            service.get(1, user)

    def test_unknown_addon_is_rejected(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = None
        with pytest.raises(AddonError):
            service.get(1, user)


class TestUpdateAddon:
    def test_updates_editable_fields(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1)

        updated = service.update(_addon(id=1, name="New name", jotform_alias="new alias"), user)

        assert updated.name == "New name"
        assert updated.jotform_alias == "new alias"

    def test_keeping_own_alias_is_not_a_duplicate(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1)
        addon_repo.find_by_alias.return_value = [_addon(id=1)]

        service.update(_addon(id=1), user)

    def test_taking_another_addons_alias_is_rejected(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1)
        addon_repo.find_by_alias.return_value = [_addon(id=2)]

        with pytest.raises(AddonError):
            service.update(_addon(id=1), user)

    def test_update_cannot_move_addon_to_another_business(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1, business_id=100)

        updated = service.update(_addon(id=1, business_id=555), user)

        assert updated.business_id == 100

    def test_update_enforces_duration_rule(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1)

        with pytest.raises(AddonError):
            service.update(_addon(id=1, has_duration=True, duration_minutes=None), user)


class TestDeactivateAddon:
    def test_deactivate_keeps_the_addon_in_the_data(self, service, addon_repo, user):
        addon_repo.get_by_id.return_value = _addon(id=1)

        result = service.deactivate(1, user)

        assert result.is_active is False
        addon_repo.update.assert_called_once()
        assert not hasattr(addon_repo, "delete") or not addon_repo.delete.called

    def test_service_offers_no_hard_delete(self, service):
        assert not hasattr(service, "delete")


class TestAddonTypeLockedOnceBooked:
    @pytest.fixture
    def stored(self, addon_repo):
        addon = _addon(id=1, has_duration=True, duration_minutes=30, has_quantity=False)
        addon_repo.get_by_id.return_value = addon
        return addon

    @pytest.fixture
    def booked(self, appointment_addon_repo):
        appointment_addon_repo.exists_for_addon.return_value = True

    def test_flags_of_a_never_booked_addon_can_change(self, service, stored, user):
        updated = service.update(_addon(id=1, has_duration=False, has_quantity=True), user)

        assert (updated.has_duration, updated.has_quantity) == (False, True)

    def test_changing_has_duration_on_a_booked_addon_is_rejected(self, service, stored, booked, addon_repo, user):
        with pytest.raises(AddonError):
            service.update(_addon(id=1, has_duration=False, has_quantity=False), user)
        addon_repo.update.assert_not_called()

    def test_changing_has_quantity_on_a_booked_addon_is_rejected(self, service, stored, booked, addon_repo, user):
        with pytest.raises(AddonError):
            service.update(_addon(id=1, has_duration=True, duration_minutes=30, has_quantity=True), user)
        addon_repo.update.assert_not_called()

    def test_other_fields_stay_editable_after_booking(self, service, stored, booked, user):
        updated = service.update(
            _addon(id=1, name="Renamed", jotform_alias="new alias", category_id=None,
                   has_duration=True, duration_minutes=45, has_quantity=False), user)

        assert (updated.name, updated.jotform_alias, updated.duration_minutes) == ("Renamed", "new alias", 45)

    def test_a_booked_addon_can_still_be_deactivated_and_reactivated(self, service, stored, booked, user):
        assert service.deactivate(1, user).is_active is False
        assert service.update(_addon(id=1, is_active=True, has_duration=True, duration_minutes=30), user).is_active is True

    def test_submitting_the_unchanged_flags_of_a_booked_addon_is_fine(self, service, stored, booked, user):
        service.update(_addon(id=1, has_duration=True, duration_minutes=30, has_quantity=False), user)

    def test_there_is_no_hard_delete_for_a_booked_addon(self, service):
        from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
        assert not hasattr(service, "delete")
        assert not hasattr(AddonRepositoryPort, "delete")
