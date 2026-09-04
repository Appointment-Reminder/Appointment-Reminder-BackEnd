from datetime import datetime
from unittest.mock import create_autospec

import pytest

from app.domain.business.errors.business_errors import InvalidBusiness, BusinessError
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_member_model import BusinessMember, MemberRole
from app.domain.business.models.business_model import Business
from app.domain.business.models.member_commission import MemberCommission
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.business.port.business_repository_port import BusinessRepositoryPort
from app.domain.business.service.business_service import BusinessService
from app.domain.user.guard.user_guard import UserGuard
from app.domain.user.models.user import User


class TestBusinessGuard:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.business_repo = create_autospec(BusinessRepositoryPort, instance=True)
        self.member_repo = create_autospec(BusinessMemberRepositoryPort, instance=True)
        self.user_repo = create_autospec(BusinessMemberRepositoryPort, instance=True)

        self.guard = BusinessGuard(
            business_repo=self.business_repo,
            business_member_repo=self.member_repo,
        )
        self.user_guard = UserGuard(user_repo=self.user_repo)

        self.service = BusinessService(
            business_repo=self.business_repo,
            member_repo=self.member_repo,
            guard=self.guard,
            user_guard=self.user_guard
        )

        self.owner = User(id=1, email="owner@studio.com", name="Owner", hashed_password="x")
        self.photographer = User(id=3, email="p@studio.com", name="P", hashed_password="x")
        self.non_admin_member = BusinessMember(business_id=10, user_id=3, role=MemberRole.PHOTOGRAPHER)
        self.admin_member = BusinessMember(business_id=10, user_id=3, role=MemberRole.ADMIN)
        self.owner_member = BusinessMember(business_id=10, user_id=3, role=MemberRole.OWNER)
        self.business = Business(
            name="studio",
            description="studio",
            owner_id=1,
            id=10
        )

    def test_ensure_exists_raise_error_if_not_exist(self):
        self.business_repo.find_by_id.return_value = None
        with pytest.raises(InvalidBusiness):
            self.guard.ensure_exists(10)

    def test_exists_return_business(self):
        self.business_repo.find_by_id.return_value = self.business
        assert self.guard.ensure_exists(10) == self.business

    def test_ensure_member_exist_raise_error_if_not_exist(self):
        self.member_repo.get_member_by_id.return_value = None
        with pytest.raises(BusinessError):
            self.guard.ensure_member_exist(10)

    def test_ensure_member_exist_return_member(self):
        self.member_repo.get_member_by_id.return_value = self.owner
        assert self.guard.ensure_member_exist(10) == self.owner

    def test_ensure_not_a_member_raise_error_if_is_a_member(self):
        self.member_repo.get_member.return_value = self.non_admin_member
        with pytest.raises(BusinessError):
            self.guard.ensure_not_a_member(business_id=10, user_id=3)

    def test_ensure_not_a_member_return_true_if_not_a_member(self):
        self.member_repo.get_member.return_value = None
        assert self.guard.ensure_not_a_member(business_id=10, user_id=1) == True

    def test_ensure_admin_or_owner_raise_error_if_is_a_member(self):
        self.member_repo.get_member.return_value = self.non_admin_member
        with pytest.raises(BusinessError):
            self.guard.ensure_admin_or_owner(business_id=10, user_id=3)

    def test_ensure_admin_or_owner_raise_return_member_if_is_admin(self):
        self.member_repo.get_member.return_value = self.admin_member
        result = self.guard.ensure_admin_or_owner(business_id=10, user_id=3)
        assert result == self.admin_member

    def test_ensure_admin_or_owner_raise_return_member_if_is_owner(self):
        self.member_repo.get_member.return_value = self.owner_member
        result = self.guard.ensure_admin_or_owner(business_id=10, user_id=3)
        assert result == self.owner_member

    def test_commission_exist_raise_error_if_none(self):
        self.member_repo.get_commission_by_id.return_value = None
        with pytest.raises(BusinessError):
            self.guard.ensure_commission_Exist(commission_id=10)

    def test_commission_exist_return_Commission(self):
        created = MemberCommission(
            id = 10,
            business_member_id= 10,
            package_id= 10,
            commission_amount= 10,
            commission_isPercentage= True,
            effective_from= datetime(year=2021, month=1, day=1),
        )
        self.member_repo.get_commission_by_id.return_value = created
        result = self.guard.ensure_commission_Exist(commission_id=10)
        assert result == created