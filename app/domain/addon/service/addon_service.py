from dataclasses import replace
from datetime import datetime
from typing import List, Optional

from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon_alias import normalize_alias
from app.domain.addon.models.addon import Addon
from app.domain.addon.models.addon_commission import AddonCommission, commission_in_effect
from app.domain.addon.models.addon_price import AddonPrice, price_in_effect
from app.domain.addon.port.addon_commission_repository_port import AddonCommissionRepositoryPort
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import MemberRole
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.addon.errors.addon_errors import AddonError, NoAddonPriceInEffect
from app.domain.user.models.user import User


class AddonService:
    """Add-on catalogue: the business-owned list of extras and their Aliases."""

    def __init__(
        self,
        addon_repo: AddonRepositoryPort,
        price_repo: AddonPriceRepositoryPort,
        commission_repo: AddonCommissionRepositoryPort,
        appointment_addon_repo: AppointmentAddonRepositoryPort,
        business_guard: BusinessGuard,
        package_guard: PackageGuard,
        addon_guard: AddonGuard,
    ):
        self.addon_repo = addon_repo
        self.price_repo = price_repo
        self.commission_repo = commission_repo
        self.appointment_addon_repo = appointment_addon_repo
        self.business_guard = business_guard
        self.package_guard = package_guard
        self.addon_guard = addon_guard

    def create(self, data: Addon, current_user: User) -> Addon:
        self.business_guard.ensure_exists(data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        addon = self._normalized(data, business_id=data.business_id, is_active=True)
        self._ensure_valid(addon)
        return self._with_current_price(self.addon_repo.create(addon))

    def list(self, business_id: int, current_user: User) -> List[Addon]:
        """The catalogue for any member: owner and admin see inactive add-ons too, the others only the active ones."""
        self.business_guard.ensure_exists(business_id)
        member = self.business_guard.ensure_is_a_member(business_id, current_user.id)
        only_active = None if self._is_admin(member) else True
        return self._with_current_prices(self.addon_repo.list_by_business(business_id, is_active=only_active))

    def get(self, addon_id: int, current_user: User) -> Addon:
        addon = self.addon_guard.ensure_addon_exist(addon_id)
        member = self.business_guard.ensure_is_a_member(addon.business_id, current_user.id)
        if not (addon.is_active or self._is_admin(member)):
            raise AddonError()
        return self._with_current_price(addon)

    def update(self, data: Addon, current_user: User) -> Addon:
        existing = self._get_for_admin(data.id, current_user)

        addon = self._normalized(data, business_id=existing.business_id, is_active=data.is_active)
        self._ensure_type_not_locked(existing, addon)
        self._ensure_valid(addon)
        return self._with_current_price(self.addon_repo.update(addon))

    def deactivate(self, addon_id: int, current_user: User) -> Addon:
        addon = self._get_for_admin(addon_id, current_user)
        return self._with_current_price(self.addon_repo.update(replace(addon, is_active=False)))

    # PRICE
    def create_price(self, data: AddonPrice, current_user: User) -> AddonPrice:
        self._get_for_admin(data.addon_id, current_user)
        if data.price < 0:
            raise AddonError()

        return self.price_repo.create(
            AddonPrice(addon_id=data.addon_id, price=data.price, effective_from=data.effective_from)
        )

    def get_current_price(self, addon_id: int, current_user: User, at: Optional[datetime] = None) -> AddonPrice:
        self._get_for_admin(addon_id, current_user)
        price = price_in_effect(self.price_repo.get_history(addon_id), at or datetime.now())
        if price is None:
            raise NoAddonPriceInEffect()
        return price

    def get_price_history(self, addon_id: int, current_user: User) -> List[AddonPrice]:
        self._get_for_admin(addon_id, current_user)
        return self.price_repo.get_history(addon_id)

    # COMMISSION
    def create_commission(self, data: AddonCommission, current_user: User) -> AddonCommission:
        addon = self._get_for_admin(data.addon_id, current_user)
        member = self.business_guard.ensure_member_exist(member_id=data.business_member_id)
        if member.business_id != addon.business_id:
            raise AddonError()
        self._ensure_commission_valid(data)

        return self.commission_repo.create(AddonCommission(
            business_member_id=data.business_member_id,
            addon_id=data.addon_id,
            commission_amount=data.commission_amount,
            commission_isPercentage=data.commission_isPercentage,
            effective_from=data.effective_from,
        ))

    def correct_commission(self, data: AddonCommission, current_user: User) -> AddonCommission:
        """Fix the amount and kind of an existing version in place. Booked Appointment Add-ons keep their frozen one."""
        stored = self.commission_repo.get_by_id(data.id) if data.id is not None else None
        if stored is None:
            raise AddonError()
        self._get_for_admin(stored.addon_id, current_user)
        self._ensure_commission_valid(data)

        return self.commission_repo.update(replace(
            stored, commission_amount=data.commission_amount, commission_isPercentage=data.commission_isPercentage))

    def get_current_commission(self, member_id: int, addon_id: int, current_user: User,
                               at: Optional[datetime] = None) -> AddonCommission:
        addon = self._get_for_admin(addon_id, current_user)
        member = self.business_guard.ensure_member_exist(member_id=member_id)
        if member.business_id != addon.business_id:
            raise AddonError()
        history = self.commission_repo.get_history(member_id, addon_id)
        return commission_in_effect(history, member_id, addon_id, at or datetime.now())

    @staticmethod
    def _is_admin(member) -> bool:
        return member.role in (MemberRole.OWNER, MemberRole.ADMIN)

    def list_member_addon_commissions(self, business_id: int, member_id: int,
                                      current_user: User) -> List[AddonCommission]:
        """The commission in effect now for each active add-on, a flat 0 where the member has no row."""
        self.business_guard.ensure_exists(business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        member = self.business_guard.ensure_member_exist(member_id=member_id)
        if member.business_id != business_id:
            raise AddonError()

        histories = self.commission_repo.get_histories_for_member(member_id)
        now = datetime.now()
        return [
            commission_in_effect(histories.get(addon.id, []), member_id, addon.id, now)
            for addon in self.addon_repo.list_by_business(business_id, is_active=True)
        ]

    def _get_for_admin(self, addon_id: int, current_user: User) -> Addon:
        addon = self.addon_guard.ensure_addon_exist(addon_id)
        self.business_guard.ensure_admin_or_owner(addon.business_id, current_user.id)
        return addon

    def _with_current_price(self, addon: Addon) -> Addon:
        return self._with_current_prices([addon])[0]

    def _with_current_prices(self, addons: List[Addon]) -> List[Addon]:
        """The addons with the price in effect now, from a single price lookup."""
        histories = self.price_repo.get_histories([a.id for a in addons])
        now = datetime.now()
        result = []
        for addon in addons:
            price = price_in_effect(histories.get(addon.id, []), now)
            result.append(replace(addon, current_price=price.price if price else None))
        return result

    def _normalized(self, data: Addon, business_id: int, is_active: bool) -> Addon:
        return Addon(
            id=data.id,
            business_id=business_id,
            name=data.name,
            jotform_alias=normalize_alias(data.jotform_alias),
            is_active=is_active,
            category_id=data.category_id,
            has_duration=data.has_duration,
            has_quantity=data.has_quantity,
            duration_minutes=data.duration_minutes if data.has_duration else None,
        )

    @staticmethod
    def _ensure_commission_valid(data: AddonCommission) -> None:
        if data.commission_amount < 0 or (data.commission_isPercentage and data.commission_amount > 100):
            raise AddonError()

    def _ensure_type_not_locked(self, existing: Addon, changed: Addon) -> None:
        """Once an Appointment Add-on references the add-on, its type is fixed: deactivate it and create a new one."""
        type_changed = (existing.has_duration, existing.has_quantity) != (changed.has_duration, changed.has_quantity)
        if type_changed and self.appointment_addon_repo.exists_for_addon(existing.id):
            raise AddonError()

    def _ensure_valid(self, addon: Addon) -> None:
        self.addon_guard.ensure_duration_rule(addon)
        self.addon_guard.ensure_alias_available(addon.business_id, addon.jotform_alias, addon.id)
        if addon.category_id is not None:
            category = self.package_guard.ensure_category_exist(addon.category_id)
            if category.business_id != addon.business_id:
                raise AddonError()
