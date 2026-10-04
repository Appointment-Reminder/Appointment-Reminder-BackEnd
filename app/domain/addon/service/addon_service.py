from dataclasses import replace
from typing import List

from app.domain.addon.guard.addon_guard import AddonGuard, normalize_alias
from app.domain.addon.models.addon import Addon
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.addon.errors.addon_errors import AddonError
from app.domain.user.models.user import User


class AddonService:
    """Add-on catalogue: the business-owned list of extras and their Aliases."""

    def __init__(
        self,
        addon_repo: AddonRepositoryPort,
        business_guard: BusinessGuard,
        package_guard: PackageGuard,
        addon_guard: AddonGuard,
    ):
        self.addon_repo = addon_repo
        self.business_guard = business_guard
        self.package_guard = package_guard
        self.addon_guard = addon_guard

    def create(self, data: Addon, current_user: User) -> Addon:
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        addon = self._normalized(data, business_id=data.business_id, is_active=True)
        self._ensure_valid(addon)
        return self.addon_repo.create(addon)

    def list(self, business_id: int, current_user: User) -> List[Addon]:
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        return self.addon_repo.list_by_business(business_id)

    def get(self, addon_id: int, current_user: User) -> Addon:
        addon = self.addon_guard.ensure_addon_exist(addon_id)
        self.business_guard.ensure_admin_or_owner(addon.business_id, current_user.id)
        return addon

    def update(self, data: Addon, current_user: User) -> Addon:
        existing = self.get(data.id, current_user)

        addon = self._normalized(data, business_id=existing.business_id, is_active=data.is_active)
        self._ensure_valid(addon)
        return self.addon_repo.update(addon)

    def deactivate(self, addon_id: int, current_user: User) -> Addon:
        addon = self.get(addon_id, current_user)
        return self.addon_repo.update(replace(addon, is_active=False))

    def _normalized(self, data: Addon, business_id: int, is_active: bool) -> Addon:
        return Addon(
            id=data.id,
            business_id=business_id,
            name=data.name,
            jotform_alias=normalize_alias(data.jotform_alias),
            is_active=is_active,
            category_id=data.category_id,
            has_duration=data.has_duration,
            has_quantity=data.has_quantity,
            duration_minutes=data.duration_minutes if data.has_duration else None,
        )

    def _ensure_valid(self, addon: Addon) -> None:
        self.addon_guard.ensure_duration_rule(addon)
        self.addon_guard.ensure_alias_available(addon.business_id, addon.jotform_alias, addon.id)
        if addon.category_id is not None:
            category = self.package_guard.ensure_category_exist(addon.category_id)
            if category.business_id != addon.business_id:
                raise AddonError()
