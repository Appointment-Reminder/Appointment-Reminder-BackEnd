from dataclasses import dataclass
from typing import Optional

from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.addon.models.addon_price import AddonPrice


@dataclass
class AppointmentAddon:
    """An Add-on booked on one appointment. Unit values are frozen at booking; totals derive from them."""
    addon_id: int
    addon_price_id: int
    quantity: int
    unit_price: float
    unit_duration: int
    unit_commission_percent: Optional[float]
    unit_commission_amount: Optional[float]
    line_total: float
    line_commission: Optional[float]
    appointment_id: Optional[int] = None
    raw_label: Optional[str] = None
    id: Optional[int] = None

    @property
    def line_duration(self) -> int:
        return self.unit_duration * self.quantity


def _line_commission(
    unit_price: float, quantity: int, percent: Optional[float], flat: Optional[float]
) -> Optional[float]:
    """A flat commission applies per unit, a percentage applies to the line total. None when unset."""
    if percent is not None:
        return unit_price * quantity * percent / 100
    if flat is not None:
        return flat * quantity
    return None


def snapshot_appointment_addon(
    addon: Addon,
    price: AddonPrice,
    commission: Optional[AddonCommission],
    quantity: int = 1,
    raw_label: Optional[str] = None,
) -> AppointmentAddon:
    """Freeze the price and commission now in effect. `commission` is None when no member is assigned (unset)."""
    percent: Optional[float] = None
    flat: Optional[float] = None
    if commission is not None:
        if commission.commission_isPercentage:
            percent = float(commission.commission_amount)
        else:
            flat = float(commission.commission_amount)

    unit_price = float(price.price)
    return AppointmentAddon(
        addon_id=addon.id,
        addon_price_id=price.id,
        quantity=quantity,
        unit_price=unit_price,
        unit_duration=(addon.duration_minutes or 0) if addon.has_duration else 0,
        unit_commission_percent=percent,
        unit_commission_amount=flat,
        line_total=unit_price * quantity,
        line_commission=_line_commission(unit_price, quantity, percent, flat),
        raw_label=raw_label,
    )


def with_quantity(line: AppointmentAddon, quantity: int) -> AppointmentAddon:
    """Same line at another quantity, recomputed from the frozen unit values (the catalogue is never re-read)."""
    return AppointmentAddon(
        id=line.id, appointment_id=line.appointment_id, addon_id=line.addon_id,
        addon_price_id=line.addon_price_id, quantity=quantity, unit_price=line.unit_price,
        unit_duration=line.unit_duration, unit_commission_percent=line.unit_commission_percent,
        unit_commission_amount=line.unit_commission_amount, raw_label=line.raw_label,
        line_total=line.unit_price * quantity,
        line_commission=_line_commission(line.unit_price, quantity, line.unit_commission_percent,
                                         line.unit_commission_amount),
    )
