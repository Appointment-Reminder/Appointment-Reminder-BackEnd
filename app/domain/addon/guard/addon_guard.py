from typing import Optional

from app.domain.addon.errors.addon_errors import AddonError
from app.domain.addon.models.addon import Addon
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort


class AddonGuard:
    def __init__(self, addon_repo: AddonRepositoryPort):
        self.addon_repo = addon_repo

    def ensure_addon_exist(self, addon_id: int) -> Addon:
        addon = self.addon_repo.get_by_id(addon_id)
        if addon is None:
            raise AddonError()
        return addon

    def ensure_alias_available(self, business_id: int, alias: str, addon_id: Optional[int] = None) -> None:
        if not alias:
            raise AddonError()
        for other in self.addon_repo.find_by_alias(business_id, alias):
            if other.id != addon_id:
                raise AddonError()

    def ensure_duration_rule(self, addon: Addon) -> None:
        if addon.has_duration and (addon.duration_minutes is None or addon.duration_minutes <= 0):
            raise AddonError()
