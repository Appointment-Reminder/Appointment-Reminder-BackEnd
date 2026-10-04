from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from app.domain.addon.models.effective import latest_in_effect


@dataclass
class AddonPrice:
    addon_id: int
    price: int
    effective_from: datetime
    id: Optional[int] = None


def price_in_effect(prices: Iterable[AddonPrice], at: datetime) -> Optional[AddonPrice]:
    """The latest price whose effective date has passed; None when there is none (no price, or only future-dated)."""
    return latest_in_effect(prices, at)
