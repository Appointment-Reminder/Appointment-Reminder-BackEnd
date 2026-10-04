from typing import Dict, Protocol, List

from app.domain.addon.models.addon_commission import AddonCommission


class AddonCommissionRepositoryPort(Protocol):
    def create(self, commission: AddonCommission) -> AddonCommission: ...
    def get_history(self, member_id: int, addon_id: int) -> List[AddonCommission]:
        """Every commission version of the member for the add-on, including future-dated ones."""
    def get_histories_for_member(self, member_id: int) -> Dict[int, List[AddonCommission]]:
        """The member's commission history on every add-on in one lookup; add-ons without a row are absent."""
