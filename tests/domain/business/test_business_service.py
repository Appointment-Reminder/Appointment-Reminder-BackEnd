from dataclasses import replace
from unittest.mock import create_autospec

import pytest
from sqlalchemy.sql.functions import current_user

from app.domain.business.errors.business_errors import BusinessError
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.models.business_invitation import BusinessMemberInvitation
from app.domain.business.models.business_member_model import MemberRole, BusinessMember
from app.domain.business.models.business_model import Business
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.business.port.business_repository_port import BusinessRepositoryPort
from app.domain.business.service.business_service import BusinessService
from app.domain.user.guard.user_guard import UserGuard
from app.domain.user.models.user import User


class TestBusinessService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.business_repo = create_autospec(BusinessRepositoryPort, instance=True)
        self.member_repo = create_autospec(BusinessMemberRepositoryPort, instance=True)
        self.user_repo = create_autospec(BusinessMemberRepositoryPort, instance=True)

        self.guard = create_autospec(BusinessGuard, instance=True)
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
class TestBusinessServiceAuthorization(TestBusinessService):

    def test_get_for_user_ensure_user_is_part_of_business(self):
        self.guard.ensure_exists.return_value = object()
        self.service.get_for_user(current_user=self.owner, is_active=None, business_id=10)
        self.guard.ensure_is_a_member.assert_called_once_with(
            business_id=10, user_id=self.owner.id
        )

    def test_update_business_check_if_user_is_admin(self):
        self.business_repo.update.return_value = self.business
        self.service.update(business_id= self.business.id, data = self.business, current_user=self.owner)
        self.guard.ensure_admin_or_owner.assert_called_once_with(business_id=self.business.id, user_id=self.owner.id)

    def test_update_business_check_if_business_exist(self):
        self.business_repo.update.return_value = self.business
        self.service.update(business_id=self.business.id, data=self.business, current_user=self.owner)
        self.guard.ensure_exists.assert_called_once_with(business_id=self.business.id)

    def test_delete_business_check_if_business_exist(self):
        self.member_repo.delete.return_value = True
        self.member_repo.get_by_business_id.return_value = []
        self.service.delete(business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_exists.assert_called_once_with(business_id=self.business.id)

    def test_delete_business_check_if_user_admin_or_owner(self):
        self.member_repo.delete.return_value = True
        self.member_repo.get_by_business_id.return_value = []
        self.service.delete(business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_admin_or_owner.assert_called_once_with(business_id=self.business.id, user_id=self.owner.id)

    def test_get_members_check_if_user_is_admin(self):
        self.member_repo.get_by_business_id.return_value = []

        self.service.get_members(business_id=10, current_user=self.owner)

        self.guard.ensure_admin_or_owner.assert_called_once_with(
            business_id=10, user_id=self.owner.id
        )

    def test_get_members_check_for_non_existing_business(self):
        self.member_repo.get_by_business_id.return_value = []
        self.service.get_members(business_id=10, current_user=self.owner)
        self.guard.ensure_exists.assert_called_once_with(
            business_id=10
        )

    def test_update_member_check_if_user_is_admin(self):
        self.service.update_member(data=self.non_admin_member, member_id=self.non_admin_member.id, business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_admin_or_owner.assert_called_once_with(business_id=self.business.id, user_id=self.owner.id)

    def test_update_member_check_if_business_exist(self):
        self.service.update_member(data=self.non_admin_member, member_id=self.non_admin_member.id, business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_exists.assert_called_once_with(business_id=self.business.id)

    def test_update_member_check_if_user_is_a_member(self):
        self.service.update_member(data=self.non_admin_member, member_id=self.non_admin_member.id,
                                   business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_member_exist.assert_called_once_with(member_id=self.non_admin_member.id)

    def test_update_member_check_if_user_is_a_member(self):
        self.guard.ensure_member_exist.return_value = self.non_admin_member
        self.service.update_member(data=self.non_admin_member, member_id=self.non_admin_member.id,
                                   business_id=self.business.id, current_user=self.owner)
        self.guard.ensure_is_a_member.assert_called_once_with(business_id = self.business.id, user_id=self.non_admin_member.user_id)

    def test_delete_member_ensure_member_exist(self):
        self.service.delete_member(business_id= self.business.id, member_id=self.non_admin_member.id, current_user = self.owner)
        self.guard.ensure_is_a_member.assert_called_once_with(business_id=self.business.id, user_id=self.non_admin_member.id)

    def test_delete_member_ensure_business_exist(self):
        self.service.delete_member(business_id=self.business.id, member_id=self.non_admin_member.id,
                                   current_user=self.owner)
        self.guard.ensure_exists.assert_called_once_with(business_id=self.business.id)

    def test_delete_member_ensure_admin_or_owner(self):
        self.service.delete_member(business_id=self.business.id, member_id=self.non_admin_member.id,
                                   current_user=self.owner)
        self.guard.ensure_admin_or_owner.assert_called_once_with(business_id=self.business.id, user_id = self.owner.id)

class TestBusinessServiceBehavior(TestBusinessService):

    def test_create_business_return_the_current_user_as_owner(self):
        self.business_repo.create.side_effect = lambda business: replace(business, id=99)
        created = self.service.create(
            data=Business(name="Sunset Studio", description=None, owner_id=None,
                          id=None, is_active=True, created_at=None, updated_at=None),
            current_user=self.owner)

        assert created.id == 99
        assert created.owner_id == self.owner.id

    def test_create_business_create_a_member_for_owner(self):
        self.business_repo.create.side_effect = lambda business: replace(business, id=99)

        saved = self.service.create(
            data=Business(name="Sunset Studio", description=None, owner_id=None,
                          id=None, is_active=True, created_at=None, updated_at=None),
            current_user=self.owner,
        )
        created_member = self.member_repo.create.call_args.args[0]
        assert created_member.business_id == 99
        assert created_member.role == MemberRole.OWNER

    def test_get_business_for_user_without_business_id(self):
        self.service.get_for_user(current_user=self.owner, is_active=None, business_id=None)
        self.business_repo.find_by_user.assert_called_once_with(user_id=self.owner.id)

    def test_update_business_return_modified_business(self):
        self.business_repo.update.side_effect = lambda business_id, business: replace(business, name="UpdatedName")
        updated = self.service.update(business_id=10, data=self.business, current_user=self.owner)
        assert updated.name == "UpdatedName"

    def test_update_delete_call_repo_delete(self):
        self.service.delete(business_id=10, current_user=self.owner)
        self.business_repo.delete.assert_called_once_with(business_id=10)

    def test_delete_all_members(self):
        self.service.delete_all_members(business_id=self.business.id, current_user=self.owner)

    def test_deletes_every_member_returned(self):
        member_a = BusinessMember(id=1, business_id=10, user_id=2, role=MemberRole.PHOTOGRAPHER)
        member_b = BusinessMember(id=2, business_id=10, user_id=3, role=MemberRole.ADMIN)
        self.member_repo.get_by_business_id.return_value = [member_a, member_b]

        self.service.delete_all_members(business_id=10, current_user=self.owner)

        assert self.member_repo.delete.call_count == 2
        self.member_repo.delete.assert_any_call(1)
        self.member_repo.delete.assert_any_call(2)

    def test_no_members_deletes_nothing(self):
        self.member_repo.get_by_business_id.return_value = []

        self.service.delete_all_members(business_id=10, current_user=self.owner)

        self.member_repo.delete.assert_not_called()

    def test_propagates_guard_rejection_without_deleting(self):
        self.guard.ensure_admin_or_owner.side_effect = BusinessError()

        with pytest.raises(BusinessError):
            self.service.delete_all_members(business_id=10, current_user=self.owner)

        self.member_repo.get_by_business_id.assert_not_called()
        self.member_repo.delete.assert_not_called()

    def test_get_members_return_member(self):
        self.member_repo.get_by_business_id.return_value = [self.non_admin_member]
        members = self.service.get_members(business_id=self.business.id, current_user=self.owner)

        assert members == [self.non_admin_member]

    def test_update_member_change_role_of_user(self):
        self.guard.ensure_member_exist.return_value = self.non_admin_member
        self.member_repo.update.side_effect = lambda  member : member
        updatedValue = BusinessMember( user_id=3, role=MemberRole.ADMIN, business_id=10)
        updatedUser = self.service.update_member(data= updatedValue,
                                   business_id=self.business.id,
                                   member_id=self.non_admin_member.id,
                                   current_user=self.owner)

        assert updatedUser.role == MemberRole.ADMIN

    def test_update_member_dont_create_new_owner(self):
        self.guard.ensure_member_exist.return_value = self.non_admin_member
        self.member_repo.update.side_effect = lambda member: member
        updatedValue = BusinessMember(user_id=3, role=MemberRole.OWNER, business_id=10)

        with pytest.raises(BusinessError):
            updatedUser = self.service.update_member(data=updatedValue,
                                                     business_id=self.business.id,
                                                     member_id=self.non_admin_member.id,
                                                     current_user=self.owner)

    def test_update_member_cant_remove_owner(self):
        self.guard.ensure_member_exist.return_value = self.owner_member
        self.member_repo.update.side_effect = lambda member: member
        updatedValue = BusinessMember(user_id=3, role=MemberRole.ADMIN, business_id=10)

        with pytest.raises(BusinessError):
            updatedUser = self.service.update_member(data=updatedValue,
                                                     business_id=self.business.id,
                                                     member_id=self.owner_member.id,
                                                     current_user=self.owner)

    def test_delete_member_Cant_delete_owner(self):
        self.guard.ensure_is_a_member.return_value = self.owner_member

        with pytest.raises(BusinessError):
            self.service.delete_member(business_id=10, member_id=10, current_user=self.owner)

    def test_delete_member_Cant_delete_self(self):
        self.guard.ensure_is_a_member.return_value = self.owner_member

        with pytest.raises(BusinessError):
            self.service.delete_member(business_id=10, member_id=self.owner_member.id, current_user=self.owner)

    def test_delete_member_return_repo_delete(self):
        self.guard.ensure_is_a_member.return_value = self.non_admin_member
        self.member_repo.delete.return_value = True
        result = self.service.delete_member(business_id=10, member_id=self.non_admin_member.id,current_user=self.owner)
        assert result == True