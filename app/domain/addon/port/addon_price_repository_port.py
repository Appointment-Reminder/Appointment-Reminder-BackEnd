from typing import Dict, Protocol, List

from app.domain.addon.models.addon_price import AddonPrice


class AddonPriceRepositoryPort(Protocol):
    def create(self, addon_price: AddonPrice) -> AddonPrice: ...
    def get_history(self, addon_id: int) -> List[AddonPrice]:
        """Every price version of the add-on, including future-dated ones."""
    def get_histories(self, addon_ids: List[int]) -> Dict[int, List[AddonPrice]]:
        """The price history of each add-on in one lookup; add-ons without a price are absent."""
