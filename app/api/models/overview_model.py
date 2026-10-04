from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class _Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HeadlineRead(_Read):
    total_income: float
    deposit_income: float
    balance_income: float
    booked_revenue: float
    appointments_made: int
    commission_payable: float
    owner_take: Optional[float]


class HeadlineChangeRead(_Read):
    total_income: Optional[float]
    deposit_income: Optional[float]
    balance_income: Optional[float]
    booked_revenue: Optional[float]
    appointments_made: Optional[float]
    commission_payable: Optional[float]
    owner_take: Optional[float]


class ComparisonRead(_Read):
    previous_from: date
    previous_to: date
    previous: HeadlineRead
    change_percent: HeadlineChangeRead


class RevenueLineRead(_Read):
    id: Optional[int]
    name: Optional[str]
    revenue: float
    count: int


class ReferralSourceRead(_Read):
    source: Optional[str]
    count: int


class BusinessFiguresRead(_Read):
    total_income: float
    deposit_income: float
    balance_income: float
    package_balance: float
    addon_income: float
    outstanding_balance: float
    booked_revenue: float
    appointments_made: int
    commission_payable: float
    owner_take: Optional[float]
    average_appointment_value: float
    cancellation_rate: float
    addon_attach_rate: float
    top_addons: List[RevenueLineRead]
    revenue_by_package: List[RevenueLineRead]
    revenue_by_category: List[RevenueLineRead]
    referral_sources: List[ReferralSourceRead]
    unresolved_addons: int
    commissions_above_balance: int


class MemberRowRead(_Read):
    member_id: Optional[int]
    name: Optional[str]
    income: float
    booked_revenue: float
    commission_earned: float
    appointments_made: int
    average_appointment_value: float
    cancellation_rate: float


class SeriesPointRead(_Read):
    start: date
    income: float
    deposit_income: float
    balance_income: float


class BusinessOverviewRead(_Read):
    business_id: int
    period_from: date
    period_to: date
    group_by: Optional[str]
    business: Optional[BusinessFiguresRead]
    members: List[MemberRowRead]
    comparison: Optional[ComparisonRead]
    series: Optional[List[SeriesPointRead]]
