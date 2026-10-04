from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from app.domain.addon.models.effective import latest_in_effect


@dataclass(frozen=True)
class AddonCommission:
    business_member_id: int
    addon_id: int
    commission_amount: int
    commission_isPercentage: bool
    effective_from: datetime
    id: Optional[int] = None


def commission_in_effect(
    history: Iterable[AddonCommission], member_id: int, addon_id: int, at: datetime
) -> AddonCommission:
    """The commission in effect, or a flat 0 when the member has no row for the add-on yet."""
    found = latest_in_effect(history, at)
    if found is not None:
        return found
    return AddonCommission(
        business_member_id=member_id, addon_id=addon_id,
        commission_amount=0, commission_isPercentage=False, effective_from=at,
    )
