from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional, Union

from app.domain.addon.guard.addon_guard import normalize_alias
from app.domain.addon.models.addon_commission import commission_in_effect
from app.domain.addon.models.addon_price import price_in_effect
from app.domain.addon.models.appointment_addon import AppointmentAddon, snapshot_appointment_addon
from app.domain.addon.port.addon_commission_repository_port import AddonCommissionRepositoryPort
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort


@dataclass
class AddonResolution:
    lines: List[AppointmentAddon] = field(default_factory=list)
    unresolved_labels: List[str] = field(default_factory=list)


def normalize_labels(raw: Union[None, str, Iterable[str]]) -> List[str]:
    """The submitted Add-on answer as a clean list of distinct labels, in submission order."""
    if raw is None:
        return []
    items = [raw] if isinstance(raw, str) else list(raw)
    labels: List[str] = []
    seen = set()
    for item in items:
        label = str(item).strip()
        key = normalize_alias(label)
        if key and key not in seen:
            seen.add(key)
            labels.append(label)
    return labels


class AddonBookingResolver:
    """Turns submitted Add-on labels into priced Appointment Add-ons.

    A label that cannot be priced never raises: it is returned as an unresolved label so the
    Package booking still goes through.
    """

    def __init__(
        self,
        addon_repo: AddonRepositoryPort,
        price_repo: AddonPriceRepositoryPort,
        commission_repo: AddonCommissionRepositoryPort,
    ):
        self.addon_repo = addon_repo
        self.price_repo = price_repo
        self.commission_repo = commission_repo

    def resolve(
        self,
        business_id: int,
        category_id: Optional[int],
        member_id: Optional[int],
        labels: Union[None, str, Iterable[str]],
        at: Optional[datetime] = None,
    ) -> AddonResolution:
        at = at or datetime.now()
        resolution = AddonResolution()
        booked_addon_ids = set()

        for label in normalize_labels(labels):
            matches = self.addon_repo.find_by_alias(business_id, normalize_alias(label))
            candidates = [a for a in matches if a.is_active]
            if len(candidates) != 1:
                resolution.unresolved_labels.append(label)
                continue

            addon = candidates[0]
            if addon.category_id is not None and addon.category_id != category_id:
                resolution.unresolved_labels.append(label)
                continue

            price = price_in_effect(self.price_repo.get_history(addon.id), at)
            if price is None:
                resolution.unresolved_labels.append(label)
                continue

            if addon.id in booked_addon_ids:
                continue
            booked_addon_ids.add(addon.id)

            commission = None
            if member_id is not None:
                commission = commission_in_effect(
                    self.commission_repo.get_history(member_id, addon.id), member_id, addon.id, at)
            resolution.lines.append(snapshot_appointment_addon(addon, price, commission))

        return resolution
