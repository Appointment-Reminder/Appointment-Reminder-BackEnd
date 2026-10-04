from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass
class AddonPrice:
    addon_id: int
    price: int
    effective_from: datetime
    id: Optional[int] = None


def price_in_effect(prices: Iterable[AddonPrice], at: datetime) -> Optional[AddonPrice]:
    """The latest price whose effective date has passed; None when there is none (no price, or only future-dated)."""
    started = [p for p in prices if p.effective_from <= at]
    return max(started, key=lambda p: p.effective_from, default=None)
