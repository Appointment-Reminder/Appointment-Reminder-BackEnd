from app.domain.addon.models.appointment_addon import AppointmentAddon


def _money(value: float) -> float:
    return round(value, 2)


def fold_in_addon(appointment, line: AppointmentAddon) -> None:
    """Add the line to the appointment totals. The package deposit never changes.

    An appointment without a price (unresolved Package) keeps its price totals unset; a missing member keeps the
    commission unset, and a line without a commission (no member when booked) adds none.
    """
    _fold(appointment, line, sign=1)


def fold_out_addon(appointment, line: AppointmentAddon) -> None:
    _fold(appointment, line, sign=-1)


def fold_in_addon_amounts(target, line: AppointmentAddon) -> None:
    """Fold only the money of the line (price, remaining, commission) into anything carrying those totals."""
    _fold_amounts(target, line, sign=1)


def _fold(appointment, line: AppointmentAddon, sign: int) -> None:
    _fold_amounts(appointment, line, sign)
    if line.duration_total:
        appointment.appointment_duration = max(0, (appointment.appointment_duration or 0) + sign * line.duration_total)


def _fold_amounts(appointment, line: AppointmentAddon, sign: int) -> None:
    if appointment.price_at_booking is not None:
        appointment.price_at_booking = _money(appointment.price_at_booking + sign * line.price_total)
    if appointment.remaining_amount is not None:
        appointment.remaining_amount = _money(appointment.remaining_amount + sign * line.price_total)
    if line.commission_total is not None:
        appointment.commission_amount_at_booking = _money(
            (appointment.commission_amount_at_booking or 0) + sign * line.commission_total)


def swap_addon_commission(appointment, old: AppointmentAddon, new: AppointmentAddon) -> None:
    """Replace the line's commission in the appointment commission total (an unset commission counts as nothing)."""
    delta = (new.commission_total or 0) - (old.commission_total or 0)
    if delta or new.commission_total is not None:
        appointment.commission_amount_at_booking = _money((appointment.commission_amount_at_booking or 0) + delta)
