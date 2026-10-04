from typing import Protocol, List

from app.domain.addon.models.addon_commission import AddonCommission


class AddonCommissionRepositoryPort(Protocol):
    def create(self, commission: AddonCommission) -> AddonCommission: ...
    def get_history(self, member_id: int, addon_id: int) -> List[AddonCommission]:
        """Every commission version of the member for the add-on, including future-dated ones."""
