# tests/domain/addon/conftest.py
import pytest
from unittest.mock import Mock

from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.models.addon import Addon
from app.domain.addon.service.addon_service import AddonService
from app.domain.package.models.package_category_model import PackageCategory


@pytest.fixture
def addon_repo():
    repo = Mock()
    repo.find_by_alias.return_value = []
    repo.create.side_effect = lambda a: Addon(**{**a.__dict__, "id": 1})
    repo.update.side_effect = lambda a: a
    return repo

@pytest.fixture
def price_repo():
    repo = Mock()
    repo.create.side_effect = lambda p: p
    repo.get_history.return_value = []
    return repo

@pytest.fixture
def commission_repo():
    repo = Mock()
    repo.create.side_effect = lambda c: c
    repo.get_history.return_value = []
    return repo

@pytest.fixture
def business_guard():
    return Mock()

@pytest.fixture
def package_guard():
    guard = Mock()
    guard.ensure_category_exist.return_value = PackageCategory(id=3, business_id=100, name="Wedding")
    return guard

@pytest.fixture
def service(addon_repo, price_repo, commission_repo, business_guard, package_guard):
    return AddonService(
        addon_repo=addon_repo,
        price_repo=price_repo,
        commission_repo=commission_repo,
        business_guard=business_guard,
        package_guard=package_guard,
        addon_guard=AddonGuard(addon_repo=addon_repo),
    )

@pytest.fixture
def user():
    return Mock(id=9)
