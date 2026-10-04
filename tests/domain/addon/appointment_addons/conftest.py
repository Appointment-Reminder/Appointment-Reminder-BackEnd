# tests/domain/addon/appointment_addons/conftest.py
"""In-memory fakes and fixtures shared by the Appointment Add-on tests (seam 1)."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.domain.addon.errors.addon_errors import AddonError, NoAddonPriceInEffect
from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission
from app.domain.addon.models.addon_price import AddonPrice
from app.domain.addon.service.appointment_addon_service import AppointmentAddonService
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.models.appointment_state_machine import AppointmentStatus
from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.models.business_member_model import MemberRole

NOW = datetime(2026, 10, 4, 12, 0)


class FakeAppointmentAddonRepo:
    def __init__(self):
        self.lines = []
        self.unresolved = []
        self._next = 1

    def add(self, line):
        line.id = self._next
        self._next += 1
        self.lines.append(line)
        return line

    def update(self, line):
        self.lines = [line if l.id == line.id else l for l in self.lines]
        return line

    def remove(self, line_id):
        self.lines = [l for l in self.lines if l.id != line_id]
        return True

    def get(self, appointment_id, addon_id):
        return next((l for l in self.lines if l.appointment_id == appointment_id and l.addon_id == addon_id), None)

    def list_for_appointment(self, appointment_id):
        return [l for l in self.lines if l.appointment_id == appointment_id]

    def list_for_appointments(self, ids):
        return {i: self.list_for_appointment(i) for i in ids}

    def exists_for_addon(self, addon_id):
        return any(l.addon_id == addon_id for l in self.lines)

    def add_unresolved(self, u):
        u.id = self._next
        self._next += 1
        self.unresolved.append(u)
        return u

    def get_unresolved(self, unresolved_id):
        return next((u for u in self.unresolved if u.id == unresolved_id), None)

    def update_unresolved(self, u):
        return u

    def list_unresolved_for_appointments(self, ids):
        return {i: [u for u in self.unresolved if u.appointment_id == i and not u.is_resolved] for i in ids}


class Catalogue:
    def __init__(self):
        self.addons = {}
        self.prices = {}
        self.commissions = {}

    def add(self, id, price=50, price_days=-10, **kw):
        values = dict(business_id=100, name=f"addon {id}", jotform_alias=f"alias {id}", is_active=True)
        values.update(kw)
        self.addons[id] = Addon(id=id, **values)
        if price is not None:
            self.prices[id] = [AddonPrice(id=id * 10, addon_id=id, price=price,
                                          effective_from=NOW + timedelta(days=price_days))]
        return self

    def commission(self, member_id, addon_id, amount, pct):
        self.commissions.setdefault((member_id, addon_id), []).append(AddonCommission(
            business_member_id=member_id, addon_id=addon_id, commission_amount=amount,
            commission_isPercentage=pct, effective_from=NOW - timedelta(days=1)))
        return self

    def reprice(self, addon_id, price):
        self.prices[addon_id].append(
            AddonPrice(id=900 + price, addon_id=addon_id, price=price, effective_from=NOW - timedelta(days=1)))


def _appointment(status=AppointmentStatus.PENDING, member_id=7, **overrides):
    values = dict(
        id=1, business_id=100, member_id=member_id, form_id=None, package_id=1, package_price_id=1,
        client_first_name="a", client_last_name="b", client_phone=None, client_email=None, referral_source=None,
        price_at_booking=500.0, deposit_amount=100.0, remaining_amount=400.0,
        commission_percent_at_booking=10.0, commission_amount_at_booking=50.0,
        appointment_date=datetime(2026, 12, 1), appointment_location=None, appointment_duration=60,
        appointment_note=None, number_of_persons=None, privacy_opt_out=None,
        status=status, created_at=NOW, updated_at=NOW,
    )
    values.update(overrides)
    return Appointment(**values)


@pytest.fixture
def catalogue():
    return Catalogue()


@pytest.fixture
def appointment():
    return _appointment()


@pytest.fixture
def appointment_repo(appointment):
    repo = Mock()
    repo.get_appointment_by_id.side_effect = lambda appointment_id, **kw: appointment if appointment_id == 1 else None
    return repo


@pytest.fixture
def lines():
    return FakeAppointmentAddonRepo()


@pytest.fixture
def business_guard():
    guard = Mock()
    guard.ensure_is_a_member.return_value = Mock(id=1, role=MemberRole.OWNER)
    return guard


@pytest.fixture
def service(appointment_repo, lines, catalogue, business_guard):
    addon_repo, price_repo, commission_repo = Mock(), Mock(), Mock()
    addon_repo.get_by_id.side_effect = lambda addon_id: catalogue.addons.get(addon_id)
    price_repo.get_history.side_effect = lambda addon_id: list(catalogue.prices.get(addon_id, []))
    commission_repo.get_history.side_effect = lambda m, a: list(catalogue.commissions.get((m, a), []))
    return AppointmentAddonService(
        appointment_repo=appointment_repo, appointment_addon_repo=lines, addon_repo=addon_repo,
        price_repo=price_repo, commission_repo=commission_repo, business_guard=business_guard,
        addon_guard=AddonGuard(addon_repo=addon_repo), clock=lambda: NOW,
    )


@pytest.fixture
def user():
    return Mock(id=9)
