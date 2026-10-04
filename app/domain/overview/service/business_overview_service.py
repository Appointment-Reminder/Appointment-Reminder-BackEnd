from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Callable, Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.errors.business_errors import UnauthorizedBusinessAction
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import BusinessMember, MemberRole
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.overview.errors.overview_errors import InvalidPeriod
from app.domain.overview.models.overview import (
    BusinessFigures, BusinessOverview, Comparison, Headline, HeadlineChange, MemberRow, PackageLabel,
    ReferralSourceLine, RevenueLine, SeriesPoint)
from app.domain.overview.port.overview_read_port import OverviewReadPort
from app.domain.user.models.user import User

PARIS = ZoneInfo("Europe/Paris")
GROUPINGS = ("day", "week", "month")
TOP_ADDONS = 10
_INACTIVE = (AppointmentStatus.CANCELED, AppointmentStatus.REFUNDED)


def _money(value: float) -> float:
    return round(value, 2)


def _paris(moment: datetime) -> datetime:
    """The wall-clock time in Paris. A naive datetime is already read as Paris time."""
    if moment.tzinfo is None:
        return moment
    return moment.astimezone(PARIS).replace(tzinfo=None)


def _day(moment: datetime) -> date:
    return _paris(moment).date()


def _is_active(a: Appointment) -> bool:
    return AppointmentStatus(a.status) not in _INACTIVE


def _balance(a: Appointment) -> float:
    return a.remaining_amount or 0.0


def _deposit_income(a: Appointment) -> float:
    """A refunded appointment returns its deposit, a canceled one keeps it (Retained Deposit)."""
    return 0.0 if AppointmentStatus(a.status) == AppointmentStatus.REFUNDED else a.deposit_amount or 0.0


def _balance_is_due(a: Appointment, now: datetime) -> bool:
    return _is_active(a) and _paris(a.appointment_date) <= now


def _percent_change(current: float, previous: float) -> Optional[float]:
    return None if not previous else round((current - previous) / previous * 100, 2)


def _rate(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def _bucket_start(day: date, group_by: str) -> date:
    if group_by == "week":
        return day - timedelta(days=day.weekday())
    if group_by == "month":
        return day.replace(day=1)
    return day


def _next_bucket(start: date, group_by: str) -> date:
    if group_by == "week":
        return start + timedelta(days=7)
    if group_by == "month":
        return (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return start + timedelta(days=1)


@dataclass
class _Totals:
    """The sums of one set of appointments (the business, or one member's bucket) over one period."""
    deposit_income: float = 0.0
    balance_income: float = 0.0
    addon_income: float = 0.0
    outstanding_balance: float = 0.0
    booked_revenue: float = 0.0
    appointments_made: int = 0
    booked: int = 0
    lost: int = 0
    commission_payable: float = 0.0
    commissions_above_balance: int = 0

    @property
    def income(self) -> float:
        return self.deposit_income + self.balance_income

    @property
    def owner_take(self) -> float:
        return self.income - self.commission_payable

    @property
    def average_value(self) -> float:
        return self.booked_revenue / self.appointments_made if self.appointments_made else 0.0

    @property
    def cancellation_rate(self) -> float:
        return _rate(self.lost, self.booked)


@dataclass
class _Day:
    deposit_income: float = 0.0
    balance_income: float = 0.0


class BusinessOverviewService:
    """How the business is doing over a period: income derived from appointment data (ADR 0002)."""

    def __init__(
        self,
        read_repo: OverviewReadPort,
        business_member_repo: BusinessMemberRepositoryPort,
        business_guard: BusinessGuard,
        clock: Callable[[], datetime] = lambda: datetime.now(PARIS),
    ):
        self.read_repo = read_repo
        self.business_member_repo = business_member_repo
        self.business_guard = business_guard
        self.clock = clock

    def overview(
        self,
        business_id: int,
        current_user: User,
        period_from: date,
        period_to: date,
        group_by: Optional[str] = None,
        member_id: Optional[int] = None,
    ) -> BusinessOverview:
        if period_from > period_to:
            raise InvalidPeriod("The start day must not be after the end day")
        if group_by is not None and group_by not in GROUPINGS:
            raise InvalidPeriod(f"Group by must be one of {', '.join(GROUPINGS)}")

        self.business_guard.ensure_exists(business_id)
        caller = self.business_guard.ensure_is_a_member(business_id, current_user.id)
        sees_business = caller.role in (MemberRole.OWNER, MemberRole.ADMIN)
        if not sees_business:
            if caller.role != MemberRole.PHOTOGRAPHER or member_id not in (None, caller.id):
                raise UnauthorizedBusinessAction(current_user.id, business_id)

        length = (period_to - period_from).days + 1
        previous_to = period_from - timedelta(days=1)
        previous_from = previous_to - timedelta(days=length - 1)

        appointments = self.read_repo.appointments_touching(
            business_id,
            datetime.combine(previous_from, time.min) - timedelta(days=1),
            datetime.combine(period_to, time.min) + timedelta(days=2),
        )
        members = self.business_member_repo.get_by_business_id(business_id)
        roles = {m.id: m.role for m in members}
        now = _paris(self.clock())

        rows = self._member_rows(appointments, members, roles, period_from, period_to, now)
        if not sees_business:
            return BusinessOverview(
                business_id=business_id, period_from=period_from, period_to=period_to, business=None,
                members=[r for r in rows if r.member_id == caller.id], group_by=group_by)

        is_owner = caller.role == MemberRole.OWNER
        totals = self._totals(appointments, roles, period_from, period_to, now)
        return BusinessOverview(
            business_id=business_id, period_from=period_from, period_to=period_to,
            business=self._business_figures(
                business_id, appointments, totals, is_owner, period_from, period_to),
            members=rows,
            comparison=self._comparison(
                appointments, roles, totals, is_owner, previous_from, previous_to, now),
            series=self._series(appointments, group_by, period_from, period_to, now) if group_by else None,
            group_by=group_by,
        )

    # PER APPOINTMENT ARITHMETIC
    @staticmethod
    def _owes_commission(a: Appointment, roles: Dict[int, MemberRole]) -> bool:
        return a.member_id is not None and roles.get(a.member_id) != MemberRole.OWNER

    def _totals(self, appointments: Iterable[Appointment], roles: Dict[int, MemberRole], start: date, end: date,
                now: datetime) -> _Totals:
        t = _Totals()
        for a in appointments:
            status = AppointmentStatus(a.status)
            if start <= _day(a.created_at) <= end:
                t.booked += 1
                if status in _INACTIVE:
                    t.lost += 1
                else:
                    t.appointments_made += 1
                    t.booked_revenue += a.price_at_booking or 0.0
                t.deposit_income += _deposit_income(a)
            if _is_active(a) and start <= _day(a.appointment_date) <= end:
                owes = self._owes_commission(a, roles)
                if _balance_is_due(a, now):
                    t.balance_income += _balance(a)
                    t.addon_income += sum(line.price_total for line in a.addons)
                    if owes:
                        t.commission_payable += a.commission_amount_at_booking or 0.0
                else:
                    t.outstanding_balance += _balance(a)
                if owes and (a.commission_amount_at_booking or 0.0) > _balance(a):
                    t.commissions_above_balance += 1
        return t

    # BUSINESS VIEW
    def _business_figures(self, business_id: int, appointments: List[Appointment], t: _Totals, is_owner: bool,
                          start: date, end: date) -> BusinessFigures:
        made = [a for a in appointments if _is_active(a) and start <= _day(a.created_at) <= end]
        packages = self.read_repo.package_labels(business_id)
        addon_names = self.read_repo.addon_names(business_id)

        by_package: Dict[Optional[int], List[float]] = defaultdict(lambda: [0.0, 0])
        by_category: Dict[Optional[int], List[float]] = defaultdict(lambda: [0.0, 0])
        by_addon: Dict[int, List[float]] = defaultdict(lambda: [0.0, 0])
        by_source: Dict[Optional[str], int] = defaultdict(int)
        with_addons = 0
        for a in made:
            addons_total = sum(line.price_total for line in a.addons)
            package_revenue = (a.price_at_booking or 0.0) - addons_total
            label = packages.get(a.package_id)
            for bucket, key in ((by_package, a.package_id), (by_category, label.category_id if label else None)):
                bucket[key][0] += package_revenue
                bucket[key][1] += 1
            for line in a.addons:
                by_addon[line.addon_id][0] += line.price_total
                by_addon[line.addon_id][1] += line.quantity
            with_addons += bool(a.addons)
            by_source[a.referral_source] += 1

        def lines(groups, name_of) -> List[RevenueLine]:
            return sorted((RevenueLine(id=key, name=name_of(key), revenue=_money(revenue), count=count)
                           for key, (revenue, count) in groups.items()), key=lambda l: -l.revenue)

        category_names = {p.category_id: p.category_name for p in packages.values()}
        return BusinessFigures(
            total_income=_money(t.income),
            deposit_income=_money(t.deposit_income),
            balance_income=_money(t.balance_income),
            package_balance=_money(t.balance_income - t.addon_income),
            addon_income=_money(t.addon_income),
            outstanding_balance=_money(t.outstanding_balance),
            booked_revenue=_money(t.booked_revenue),
            appointments_made=t.appointments_made,
            commission_payable=_money(t.commission_payable),
            owner_take=_money(t.owner_take) if is_owner else None,
            average_appointment_value=_money(t.average_value),
            cancellation_rate=t.cancellation_rate,
            addon_attach_rate=_rate(with_addons, len(made)),
            top_addons=lines(by_addon, addon_names.get)[:TOP_ADDONS],
            revenue_by_package=lines(by_package, lambda k: packages[k].name if k in packages else None),
            revenue_by_category=lines(by_category, category_names.get),
            referral_sources=[ReferralSourceLine(source=s, count=c) for s, c in
                              sorted(by_source.items(), key=lambda item: -item[1])],
            unresolved_addons=self.read_repo.unresolved_addon_count(business_id),
            commissions_above_balance=t.commissions_above_balance,
        )

    # MEMBER ROWS
    def _member_rows(self, appointments: List[Appointment], members: List[BusinessMember],
                     roles: Dict[int, MemberRole], start: date, end: date, now: datetime) -> List[MemberRow]:
        grouped: Dict[Optional[int], List[Appointment]] = defaultdict(list)
        for a in appointments:
            grouped[a.member_id].append(a)
        names = {m.id: (m.user.name if m.user else None) for m in members}
        keys = [m.id for m in members] + [k for k in grouped if k is not None and k not in names] + [None]

        rows = []
        for key in keys:
            t = self._totals(grouped.get(key, []), roles, start, end, now)
            rows.append(MemberRow(
                member_id=key, name=names.get(key), income=_money(t.income), booked_revenue=_money(t.booked_revenue),
                commission_earned=_money(t.commission_payable), appointments_made=t.appointments_made,
                average_appointment_value=_money(t.average_value), cancellation_rate=t.cancellation_rate))
        return rows

    # COMPARISON
    def _headline(self, t: _Totals, is_owner: bool) -> Headline:
        return Headline(
            total_income=_money(t.income), deposit_income=_money(t.deposit_income),
            balance_income=_money(t.balance_income), booked_revenue=_money(t.booked_revenue),
            appointments_made=t.appointments_made, commission_payable=_money(t.commission_payable),
            owner_take=_money(t.owner_take) if is_owner else None)

    def _comparison(self, appointments: List[Appointment], roles: Dict[int, MemberRole], current: _Totals,
                    is_owner: bool, start: date, end: date, now: datetime) -> Comparison:
        now_headline = self._headline(current, is_owner)
        before = self._headline(self._totals(appointments, roles, start, end, now), is_owner)
        change = HeadlineChange(**{
            name: _percent_change(getattr(now_headline, name), getattr(before, name))
            for name in vars(HeadlineChange()) if getattr(before, name) is not None})
        return Comparison(previous_from=start, previous_to=end, previous=before, change_percent=change)

    # TIME SERIES
    def _series(self, appointments: List[Appointment], group_by: str, start: date, end: date,
                now: datetime) -> List[SeriesPoint]:
        buckets: Dict[date, _Day] = {}
        cursor = _bucket_start(start, group_by)
        while cursor <= end:
            buckets[cursor] = _Day()
            cursor = _next_bucket(cursor, group_by)

        for a in appointments:
            booked = _day(a.created_at)
            if start <= booked <= end:
                buckets[_bucket_start(booked, group_by)].deposit_income += _deposit_income(a)
            shoot = _day(a.appointment_date)
            if start <= shoot <= end and _balance_is_due(a, now):
                buckets[_bucket_start(shoot, group_by)].balance_income += _balance(a)

        return [SeriesPoint(start=key, income=_money(b.deposit_income + b.balance_income),
                            deposit_income=_money(b.deposit_income), balance_income=_money(b.balance_income))
                for key, b in buckets.items()]
