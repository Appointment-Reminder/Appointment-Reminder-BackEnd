# app/domain/Jotform/service/jotform_submission_assembler.py
from dataclasses import dataclass
from typing import Optional

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


def resolve_booking_context(
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