from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Headline:
    """The headline figures compared with the previous period. `owner_take` is None unless the caller is the owner."""
    total_income: float = 0.0
    deposit_income: float = 0.0
    balance_income: float = 0.0
    booked_revenue: float = 0.0
    appointments_made: int = 0
    commission_payable: float = 0.0
    owner_take: Optional[float] = None


@dataclass
class HeadlineChange:
    """Percentage change of each headline figure, None where the previous value is 0."""
    total_income: Optional[float] = None
    deposit_income: Optional[float] = None
    balance_income: Optional[float] = None
    booked_revenue: Optional[float] = None
    appointments_made: Optional[float] = None
    commission_payable: Optional[float] = None
    owner_take: Optional[float] = None


@dataclass
class Comparison:
    previous_from: date
    previous_to: date
    previous: Headline
    change_percent: HeadlineChange


@dataclass
class RevenueLine:
    id: Optional[int]
    name: Optional[str]
    revenue: float
    count: int


@dataclass
class ReferralSourceLine:
    source: Optional[str]
    count: int


@dataclass
class BusinessFigures:
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
    top_addons: List[RevenueLine] = field(default_factory=list)
    revenue_by_package: List[RevenueLine] = field(default_factory=list)
    revenue_by_category: List[RevenueLine] = field(default_factory=list)
    referral_sources: List[ReferralSourceLine] = field(default_factory=list)
    unresolved_addons: int = 0
    commissions_above_balance: int = 0


@dataclass
class MemberRow:
    """One member's results. `member_id` is None on the Unassigned row."""
    member_id: Optional[int]
    name: Optional[str]
    income: float
    booked_revenue: float
    commission_earned: float
    appointments_made: int
    average_appointment_value: float
    cancellation_rate: float


@dataclass
class SeriesPoint:
    start: date
    income: float
    deposit_income: float
    balance_income: float


@dataclass
class BusinessOverview:
    business_id: int
    period_from: date
    period_to: date
    business: Optional[BusinessFigures]
    members: List[MemberRow]
    comparison: Optional[Comparison] = None
    series: Optional[List[SeriesPoint]] = None
    group_by: Optional[str] = None


@dataclass
class PackageLabel:
    name: str
    category_id: Optional[int]
    category_name: Optional[str]
