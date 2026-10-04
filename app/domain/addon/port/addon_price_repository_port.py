from typing import Protocol, List

from app.domain.addon.models.addon_price import AddonPrice


class AddonPriceRepositoryPort(Protocol):
    def create(self, addon_price: AddonPrice) -> AddonPrice: ...
    def get_history(self, addon_id: int) -> List[AddonPrice]:
        """Every price version of the add-on, including future-dated ones."""
