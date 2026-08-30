import pytest
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.service.business_service import BusinessService
from app.domain.business.models.business_model import Business
from app.domain.business.models.business_member_model import BusinessMember
from app.domain.user.guard.user_guard import UserGuard
from app.domain.user.models.user import User


class FakeBusinessRepo:
    def __init__(self):
        self._rows = {}
        self._next_id = 1

    def create(self, business: Business) -> Business:
        from dataclasses import replace
        saved = replace(business, id=self._next_id)
        self._rows[saved.id] = saved
        self._next_id += 1
        return saved

    def find_by_id(self, business_id: int) -> Business:
        return self._rows.get(business_id)


class FakeBusinessMemberRepo:
    def __init__(self):
        self._rows = {}
        self._next_id = 1

    def create(self, member: BusinessMember) -> BusinessMember:
        member.id = self._next_id
        self._rows[member.id] = member
        self._next_id += 1
        return member

    def get_member(self, business_id: int, user_id: int) -> BusinessMember:
        return next(
            (m for m in self._rows.values()
             if m.business_id == business_id and m.user_id == user_id and m.is_active),
            None,
        )

    def get_by_business_id(self, business_id: int):
        return [m for m in self._rows.values() if m.business_id == business_id]


class FakeUserRepo:
    def __init__(self):
        self._users = {}

    def get_by_email(self, email: str) -> User:
        return self._users.get(email)


@pytest.fixture
def business_repo():
    return FakeBusinessRepo()

@pytest.fixture
def member_repo():
    return FakeBusinessMemberRepo()

@pytest.fixture
def user_repo():
    return FakeUserRepo()

@pytest.fixture
def business_guard(business_repo, member_repo):
    return BusinessGuard(business_repo=business_repo, business_member_repo=member_repo)

@pytest.fixture
def user_guard(user_repo):
    return UserGuard(user_repo=user_repo)

@pytest.fixture
def business_service(business_repo, member_repo, business_guard, user_guard):
    return BusinessService(
        business_repo=business_repo,
        member_repo=member_repo,
        guard=business_guard,
        user_guard=user_guard,
    )

@pytest.fixture
def current_user():
    return User(id=1, email="owner@studio.com", name="Owner", hashed_password="x")