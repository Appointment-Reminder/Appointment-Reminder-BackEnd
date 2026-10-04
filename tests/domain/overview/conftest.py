# tests/domain/overview/conftest.py
"""In-memory fakes and builders for the business overview tests (single seam: the overview service)."""
import itertools
import pytest
from datetime import date, datetime
from unittest.mock import Mock

from app.domain.addon.models.appointment_addon import AppointmentAddon
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.models.business_member_model import BusinessMember, MemberRole
from app.domain.overview.models.overview import PackageLabel
from app.domain.overview.service.business_overview_service import BusinessOverviewService
from app.domain.user.models.user import User

NOW = datetime(2026, 10, 15, 12, 0)
PERIOD = (date(2026, 10, 1), date(2026, 10, 31))

_ids = itertools.count(1)


def appointment(booked=datetime(2026, 10, 2, 10), on=datetime(2026, 10, 10, 10), status=AppointmentStatus.PENDING,
                price=250.0, deposit=50.0, commission=70.0, member_id=7, package_id=1, addons=(),
                referral_source=None, **overrides):
    """A frozen appointment: `price` includes the add-ons, `remaining` is price minus deposit."""
    values = dict(
        id=next(_ids), business_id=100, member_id=member_id, form_id=None, package_id=package_id, package_price_id=1,
        client_first_name="a", client_last_name="b", client_phone=None, client_email=None,
        referral_source=referral_source, price_at_booking=price, deposit_amount=deposit,
        remaining_amount=price - deposit, commission_percent_at_booking=None, commission_amount_at_booking=commission,
        appointment_date=on, appointment_location=None, appointment_duration=60, appointment_note=None,
        number_of_persons=None, privacy_opt_out=None, status=status, created_at=booked, updated_at=booked,
        addons=list(addons),
    )
    values.update(overrides)
    return Appointment(**values)


def line(addon_id=1, total=30.0, quantity=1):
    return AppointmentAddon(
        addon_id=addon_id, addon_price_id=1, quantity=quantity, unit_price=total / quantity, unit_duration=0,
        unit_commission_percent=None, unit_commission_amount=None, price_total=total, commission_total=None)


class FakeOverviewRead:
    def __init__(self):
        self.appointments = []
        self.unresolved = 0
        self.packages = {1: PackageLabel("Wedding Gold", 3, "Wedding"), 2: PackageLabel("Portrait", 4, "Family")}
        self.addons = {1: "Album", 2: "Extra hour"}

    def appointments_touching(self, business_id, start, end):
        naive = lambda moment: moment.replace(tzinfo=None)
        return [a for a in self.appointments if a.business_id == business_id and (
            start <= naive(a.created_at) < end or start <= naive(a.appointment_date) < end)]

    def package_labels(self, business_id):
        return self.packages

    def addon_names(self, business_id):
        return self.addons

    def unresolved_addon_count(self, business_id):
        return self.unresolved


class FakeMembers:
    def __init__(self, members):
        self.members = members

    def get_by_business_id(self, business_id):
        return [m for m in self.members if m.business_id == business_id]


def _member(id, role, name):
    return BusinessMember(id=id, business_id=100, user_id=id + 50, role=role, user=User(
        email=f"{name}@x.com", name=name, hashed_password="x", id=id + 50))


@pytest.fixture
def read():
    return FakeOverviewRead()


@pytest.fixture
def members():
    return [_member(1, MemberRole.OWNER, "Olivia"), _member(2, MemberRole.ADMIN, "Adam"),
            _member(7, MemberRole.PHOTOGRAPHER, "Paula"), _member(8, MemberRole.PHOTOGRAPHER, "Pierre")]


@pytest.fixture
def caller(members):
    """Whoever is asking; tests pick the role with `as_member`."""
    state = {"member": members[0]}
    return state


@pytest.fixture
def as_member(caller, members):
    def pick(member_id):
        caller["member"] = next(m for m in members if m.id == member_id)
    return pick


@pytest.fixture
def business_guard(caller):
    guard = Mock()

    def ensure_is_a_member(business_id, user_id):
        member = caller["member"]
        if business_id != member.business_id or user_id != member.user_id:
            raise BusinessError()
        return member
    guard.ensure_is_a_member.side_effect = ensure_is_a_member
    return guard


@pytest.fixture
def service(read, members, business_guard):
    return BusinessOverviewService(
        read_repo=read, business_member_repo=FakeMembers(members), business_guard=business_guard, clock=lambda: NOW)


class _CurrentUser:
    def __init__(self, caller):
        self._caller = caller

    @property
    def id(self):
        return self._caller["member"].user_id


@pytest.fixture
def user(caller):
    return _CurrentUser(caller)


@pytest.fixture
def overview(service, user):
    """overview(period=PERIOD, **kw) -> BusinessOverview as the current caller."""
    def run(period=PERIOD, business_id=100, **kw):
        return service.overview(business_id=business_id, current_user=user, period_from=period[0],
                                period_to=period[1], **kw)
    return run
