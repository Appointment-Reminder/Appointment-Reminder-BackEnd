# tests/domain/addon/test_appointment_addon_edits.py
"""Seam 1: add, remove and change the quantity of Appointment Add-ons on an existing appointment."""
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


def _totals(a):
    return (a.price_at_booking, a.remaining_amount, a.commission_amount_at_booking, a.appointment_duration)


class TestAddAddon:
    def test_snapshots_the_current_price_and_the_assigned_members_commission(
        self, service, catalogue, appointment, user
    ):
        catalogue.add(1, price=50).commission(7, 1, 10, pct=True)

        result = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        line = result.addons[0]
        assert (line.addon_id, line.addon_price_id, line.quantity) == (1, 10, 1)
        assert (line.unit_price, line.line_total) == (50.0, 50.0)
        assert (line.unit_commission_percent, line.line_commission) == (10.0, 5.0)
        assert line.appointment_id == 1

    def test_updates_the_appointment_totals_and_persists_them(
        self, service, catalogue, appointment, appointment_repo, user
    ):
        catalogue.add(1, price=50, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)

        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        assert _totals(appointment) == (550.0, 450.0, 55.0, 90)
        assert appointment.deposit_amount == 100.0
        appointment_repo.update_totals.assert_called_with(appointment)

    def test_quantity_scales_the_line(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50, has_quantity=True, has_duration=True, duration_minutes=30).commission(7, 1, 4, pct=False)

        line = service.add_addon(100, 1, addon_id=1, quantity=3, current_user=user).addons[0]

        assert (line.line_total, line.line_commission) == (150.0, 12.0)
        assert _totals(appointment) == (650.0, 550.0, 62.0, 150)

    def test_without_an_assigned_member_the_addon_commission_is_unset(self, service, catalogue, appointment, user):
        appointment.member_id = None
        appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
        catalogue.add(1, price=50).commission(7, 1, 10, pct=True)

        line = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user).addons[0]

        assert (line.unit_commission_percent, line.unit_commission_amount, line.line_commission) == (None, None, None)
        assert appointment.commission_amount_at_booking == 50.0
        assert appointment.price_at_booking == 550.0

    def test_adding_an_addon_already_on_the_appointment_is_rejected(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        assert appointment.price_at_booking == 550.0

    def test_an_addon_with_no_price_in_effect_is_rejected(self, service, catalogue, appointment, user):
        catalogue.add(1, price=None)
        with pytest.raises(NoAddonPriceInEffect):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        catalogue.add(2, price=50, price_days=+5)
        with pytest.raises(NoAddonPriceInEffect):
            service.add_addon(100, 1, addon_id=2, quantity=1, current_user=user)
        assert appointment.price_at_booking == 500.0

    def test_an_inactive_addon_is_rejected(self, service, catalogue, user):
        catalogue.add(1, price=50, is_active=False)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_unknown_addon_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=404, quantity=1, current_user=user)

    def test_an_addon_of_another_business_is_rejected(self, service, catalogue, user):
        catalogue.add(1, price=50, business_id=555)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_quantity_below_one_is_rejected(self, service, catalogue, user, quantity):
        catalogue.add(1, price=50, has_quantity=True)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=quantity, current_user=user)

    def test_quantity_other_than_one_is_rejected_for_an_addon_without_quantity(self, service, catalogue, user):
        catalogue.add(1, price=50, has_quantity=False)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=2, current_user=user)


class TestChangeQuantity:
    @pytest.fixture(autouse=True)
    def _booked(self, service, catalogue, user):
        catalogue.add(1, price=50, has_quantity=True, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)
        catalogue.add(2, price=20, has_quantity=True).commission(7, 2, 4, pct=False)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        service.add_addon(100, 1, addon_id=2, quantity=1, current_user=user)

    def test_doubling_the_quantity_doubles_the_line_and_the_totals(self, service, appointment, user):
        service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)

        assert _totals(appointment) == (620.0, 520.0, 64.0, 120)   # 500+100+20 / 400+120 / 50+10+4 / 60+60

    def test_it_uses_the_frozen_unit_price_even_if_the_catalogue_price_changed(
        self, service, catalogue, appointment, user
    ):
        catalogue.reprice(1, 500)

        line = next(l for l in service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user).addons
                    if l.addon_id == 1)

        assert (line.unit_price, line.line_total, line.addon_price_id) == (50.0, 100.0, 10)
        assert appointment.price_at_booking == 620.0

    def test_a_flat_commission_scales_with_quantity_and_a_percentage_follows_the_line_total(
        self, service, appointment, user
    ):
        result = service.set_quantity(100, 1, addon_id=2, quantity=3, current_user=user)
        flat = next(l for l in result.addons if l.addon_id == 2)
        assert flat.line_commission == 12.0

        result = service.set_quantity(100, 1, addon_id=1, quantity=4, current_user=user)
        percent = next(l for l in result.addons if l.addon_id == 1)
        assert (percent.line_total, percent.line_commission) == (200.0, 20.0)
        assert appointment.commission_amount_at_booking == 50.0 + 20.0 + 12.0

    def test_going_back_down_restores_the_totals(self, service, appointment, user):
        service.set_quantity(100, 1, addon_id=1, quantity=5, current_user=user)
        service.set_quantity(100, 1, addon_id=1, quantity=1, current_user=user)

        assert _totals(appointment) == (570.0, 470.0, 59.0, 90)

    @pytest.mark.parametrize("quantity", [0, -3])
    def test_quantity_below_one_is_rejected_and_nothing_changes(self, service, appointment, lines, user, quantity):
        before = _totals(appointment)
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=1, quantity=quantity, current_user=user)
        assert _totals(appointment) == before
        assert lines.get(1, 1).quantity == 1

    def test_quantity_other_than_one_is_rejected_for_an_addon_without_quantity(
        self, service, catalogue, user
    ):
        catalogue.add(3, price=10, has_quantity=False)
        service.add_addon(100, 1, addon_id=3, quantity=1, current_user=user)

        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=3, quantity=2, current_user=user)

    def test_changing_the_quantity_of_an_addon_not_on_the_appointment_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=99, quantity=2, current_user=user)


class TestRemoveAddon:
    def test_removing_updates_the_totals_and_the_duration(self, service, catalogue, appointment, lines, user):
        catalogue.add(1, price=50, has_duration=True, duration_minutes=30).commission(7, 1, 10, pct=True)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        result = service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert result.addons == []
        assert lines.lines == []
        assert _totals(appointment) == (500.0, 400.0, 50.0, 60)

    def test_removing_a_quantified_line_removes_all_of_its_units(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50, has_quantity=True).commission(7, 1, 4, pct=False)
        service.add_addon(100, 1, addon_id=1, quantity=3, current_user=user)

        service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert _totals(appointment) == (500.0, 400.0, 50.0, 60)

    def test_remove_then_re_add_takes_the_current_catalogue_price(self, service, catalogue, appointment, user):
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        catalogue.reprice(1, 80)

        service.remove_addon(100, 1, addon_id=1, current_user=user)
        line = service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user).addons[0]

        assert (line.unit_price, line.addon_price_id) == (80.0, 980)
        assert appointment.price_at_booking == 580.0

    def test_removing_an_addon_not_on_the_appointment_is_rejected(self, service, user):
        with pytest.raises(AddonError):
            service.remove_addon(100, 1, addon_id=1, current_user=user)

    def test_removal_without_commission_on_the_line_leaves_the_appointment_commission_alone(
        self, service, catalogue, appointment, user
    ):
        appointment.member_id = None
        appointment.status = AppointmentStatus.NEEDS_ASSIGNMENT
        catalogue.add(1, price=50)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

        service.remove_addon(100, 1, addon_id=1, current_user=user)

        assert appointment.commission_amount_at_booking == 50.0


EDITABLE = ["new", "needs_assignment", "pending", "pending_selection", "pending_editing", "pending_review"]
CLOSED = ["completed", "canceled", "refunded"]


class TestStatusGuards:
    @pytest.fixture(autouse=True)
    def _catalogue(self, catalogue):
        catalogue.add(1, price=50, has_quantity=True)

    @pytest.mark.parametrize("status", EDITABLE)
    def test_edits_are_allowed_until_pending_review(self, service, appointment, user, status):
        appointment.status = AppointmentStatus(status)

        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)
        service.remove_addon(100, 1, addon_id=1, current_user=user)

    @pytest.mark.parametrize("status", CLOSED)
    def test_edits_are_rejected_on_closed_appointments(self, service, appointment, lines, user, status):
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        appointment.status = AppointmentStatus(status)
        before = _totals(appointment)

        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)
        with pytest.raises(AddonError):
            service.set_quantity(100, 1, addon_id=1, quantity=2, current_user=user)
        with pytest.raises(AddonError):
            service.remove_addon(100, 1, addon_id=1, current_user=user)
        assert _totals(appointment) == before
        assert len(lines.lines) == 1


class TestAccess:
    @pytest.fixture(autouse=True)
    def _catalogue(self, catalogue):
        catalogue.add(1, price=50)

    def test_a_non_member_is_rejected(self, service, business_guard, user):
        business_guard.ensure_is_a_member.side_effect = BusinessError()
        with pytest.raises(BusinessError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_the_assigned_photographer_may_edit(self, service, business_guard, user):
        business_guard.ensure_is_a_member.return_value = Mock(id=7, role=MemberRole.PHOTOGRAPHER)
        service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_another_photographer_may_not_edit(self, service, business_guard, user):
        business_guard.ensure_is_a_member.return_value = Mock(id=8, role=MemberRole.PHOTOGRAPHER)
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_appointment_of_another_business_is_not_found(self, service, appointment, user):
        appointment.business_id = 555
        with pytest.raises(AddonError):
            service.add_addon(100, 1, addon_id=1, quantity=1, current_user=user)

    def test_an_unknown_appointment_is_not_found(self, service, user):
        with pytest.raises(AddonError):
            service.add_addon(100, 404, addon_id=1, quantity=1, current_user=user)
