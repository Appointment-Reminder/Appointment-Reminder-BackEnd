# app/domain/Jotform/service/jotform_submission_assembler.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional, Union

from app.domain.addon.models.appointment_addon import AppointmentAddon
from app.domain.addon.models.appointment_totals import fold_in_addon_amounts
from app.domain.addon.service.addon_booking import AddonBookingResolver
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.package.port.package_repository_port import PackageRepositoryPort
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort
from app.domain.Jotform.guard.jotform_guard import JotformGuard


@dataclass
class ResolvedBookingContext:
    """What we managed to resolve from the submission — None fields mean unresolved -> needs_assignment"""
    package_id: Optional[int]
    package_duration: Optional[int]
    category_id: Optional[int]
    member_id: Optional[int]
    package_price_id: Optional[int]
    price_at_booking: Optional[float]
    deposit_amount: Optional[float]
    remaining_amount: Optional[float]
    commission_percent_at_booking: Optional[float]
    commission_amount_at_booking: Optional[float]
    fully_resolved: bool
    addons: List[AppointmentAddon] = field(default_factory=list)
    unresolved_addon_labels: List[str] = field(default_factory=list)
    addon_duration: int = 0

    @property
    def appointment_duration(self) -> Optional[int]:
        if self.package_duration is None and self.addon_duration == 0:
            return None
        return (self.package_duration or 0) + self.addon_duration


def resolve_booking_context(
    business_id: int,
    form_id: int,
    package_alias_raw: str,
    package_guard: PackageGuard,
    jotform_guard: JotformGuard,
    member_repo: BusinessMemberRepositoryPort,
    price_repo: PackagePriceRepositoryPort,
    addon_labels: Union[None, str, Iterable[str]] = None,
    addon_resolver: Optional[AddonBookingResolver] = None,
    now: Optional[datetime] = None,
) -> ResolvedBookingContext:
    """Resolve the Package, member, price and commission, then the submitted Add-ons.

    Add-on problems never affect `fully_resolved`: they only end up as unresolved labels.
    """
    booking = _resolve_package_context(
        business_id, form_id, package_alias_raw, package_guard, jotform_guard, member_repo, price_repo)
    if addon_resolver is None:
        return booking

    resolution = addon_resolver.resolve(
        business_id=business_id, category_id=booking.category_id, member_id=booking.member_id,
        labels=addon_labels, at=now,
    )
    booking.addons = resolution.lines
    booking.unresolved_addon_labels = resolution.unresolved_labels
    for line in resolution.lines:
        booking.addon_duration += line.line_duration
        fold_in_addon_amounts(booking, line)
    return booking


def _resolve_package_context(
    business_id: int,
    form_id: int,
    package_alias_raw: str,
    package_guard: PackageGuard,
    jotform_guard: JotformGuard,
    member_repo: BusinessMemberRepositoryPort,
    price_repo: PackagePriceRepositoryPort,
) -> ResolvedBookingContext:

    package = package_guard.resolve_package_by_submission_alias(business_id, package_alias_raw)
    print(f" package : {package}")
    if package is None:
        return ResolvedBookingContext(
            package_id=None, package_duration= 0 ,category_id=None, member_id=None, package_price_id=None,
            price_at_booking=None, deposit_amount=None, remaining_amount=None,
            commission_percent_at_booking=None, commission_amount_at_booking=None,
            fully_resolved=False,
        )

    assignment = jotform_guard.resolve_assignment_or_unknown(form_id, package.category_id)
    if assignment is None:
        return ResolvedBookingContext(
            package_id=package.id, package_duration= package.package_duration, category_id=package.category_id, member_id=None, package_price_id=None,
            price_at_booking=None, deposit_amount=None, remaining_amount=None,
            commission_percent_at_booking=None, commission_amount_at_booking=None,
            fully_resolved=False,
        )

    current_price = price_repo.get_current_price(package.id)
    if current_price is None:
        return ResolvedBookingContext(
            package_id=package.id, package_duration= package.package_duration, category_id=package.category_id, member_id=assignment.business_member_id,
            package_price_id=None,
            price_at_booking=None, deposit_amount=None, remaining_amount=None,
            commission_percent_at_booking=None, commission_amount_at_booking=None,
            fully_resolved=False,
        )

    commission = member_repo.get_current_commission(assignment.business_member_id, package.id)

    commission_percent = None
    commission_amount = 0.0
    if commission is not None:
        if commission.commission_isPercentage:
            commission_percent = float(commission.commission_amount)
            commission_amount = current_price.total_price * (commission.commission_amount / 100)
        else:
            commission_amount = float(commission.commission_amount)

    return ResolvedBookingContext(
        package_id=package.id,
        package_duration= package.package_duration,
        category_id=package.category_id,
        member_id=assignment.business_member_id,
        package_price_id=current_price.id,
        price_at_booking=float(current_price.total_price),
        deposit_amount=float(current_price.deposit_amount),
        remaining_amount=float(current_price.remaining_amount),
        commission_percent_at_booking=commission_percent,
        commission_amount_at_booking=commission_amount,
        fully_resolved=True,
    )