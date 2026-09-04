# conftest.py
import pytest
from unittest.mock import create_autospec

from app.domain.business.port.business_repository_port import BusinessRepositoryPort
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.service.business_service import BusinessService
from app.domain.user.guard.user_guard import UserGuard
from app.domain.user.port.user_repository_port import UserRepositoryPort


@pytest.fixture
def business_repo():
    return create_autospec(BusinessRepositoryPort, instance=True)

@pytest.fixture
def member_repo():
    return create_autospec(BusinessMemberRepositoryPort, instance=True)

@pytest.fixture
def user_repo():
    return create_autospec(UserRepositoryPort, instance=True)

@pytest.fixture
def business_guard(business_repo, member_repo):
    return BusinessGuard(business_repo=business_repo, business_member_repo=member_repo)

@pytest.fixture
def user_guard(user_repo):
    return UserGuard(user_repo=user_repo)

@pytest.fixture
def business_service(business_repo, member_repo, business_guard, user_guard):
    return BusinessService(business_repo=business_repo, member_repo=member_repo,
                           guard=business_guard, user_guard=user_guard)