from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.sql.functions import current_user

from app.models.business_model import BusinessCreate
from app.repositories.business_repository import BusinessRepository
from app.db.models.business import Business
from app.services import business_service
from app.db.models.business_member import BusinessMember, MemberRole
from app.db.models.user import User


@pytest.fixture
def business_repo():
    return Mock()

@pytest.fixture
def member_repo():
    return Mock()

@pytest.fixture
def fake_business():
    b = Business(name="Test", owner_id=1)
    b.id = 1
    b.is_active = True
    b.description = None
    b.created_at = datetime.utcnow()
    b.updated_at = datetime.utcnow()
    return b


def test_create_business(business_repo, member_repo, fake_business):
    business_repo.find_by_name.return_value = None
    business_repo.create.return_value = fake_business

    current_user = User(id=42, name="Test")
    member_repo.create.return_value = fake_business
    result = business_service.create_business(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_data = BusinessCreate(name="Test"),
    )

    business_repo.create.assert_called_once()
    member_repo.create.assert_called_once()

    created_member: BusinessMember = member_repo.create.call_args[0][0]
    assert created_member.role == MemberRole.OWNER
    assert created_member.user_id == 42
    assert result.name == "Test"

def test_get_my_business(business_repo, member_repo, fake_business):
    pass

def test_get_my_business_without_business(business_repo, member_repo, fake_business):
    pass

def test_get_business_by_id(business_repo, member_repo, fake_business):
    pass

def test_get_business_by_id_without_business(business_repo, member_repo, fake_business):
    pass

def test_update_business(business_repo, member_repo, fake_business):
    pass

def test_update_business_call_check_business_exist(business_repo, member_repo, fake_business):
    pass

def test_update_business_call_check_is_user_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member_call_check_business_exist(business_repo, member_repo, fake_business):
    pass

def test_delete_all_members_for_business_id_call_is_user_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_delete_business(business_repo, member_repo, fake_business):
    pass

def test_delete_business_call_check_business_exist(business_repo, member_repo, fake_business):
    pass

def test_delete_business_call_is_user_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_delete_busines_call_delete_all_business_members_for_business_id(business_repo, member_repo, fake_business):
    pass

def tes_delete_business_call_business_repo_delete():
    pass

def test_if_business_exist_return_true_if_business_exist_for_user(business_repo, member_repo, fake_business):
    pass

def test_if_business_exist_raise_exception_if_business_dont_exist_for_user(business_repo, member_repo, fake_business):
    pass

def test_check_if_user_is_admin_or_owne_raise_exception_if_user_is_not_adming_or_owner(business_repo, member_repo, fake_business):
    pass

def test_check_if_user_is_admin_or_owner_dont_raise_exception_if_user_is_not_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_invite_business_member():
    pass

def test_get_business_member_list_check_if_business_exist_for_user(business_repo, member_repo, fake_business):
    pass

def test_get_business_member_list_return_member_list(business_repo, member_repo, fake_business):
    pass

def test_get_business_member_list_return_empty_list_if_no_member(business_repo, member_repo, fake_business):
    pass

def test_update_business_member_check_if_business_exist(business_repo, member_repo, fake_business):
    pass

def test_update_business_member_check_if_user_is_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_update_business_member_raise_exception_if_user_update_to_owner_by_admin(business_repo, member_repo, fake_business):
    pass

def test_update_business_member_raise_exception_if_change_owner_role(business_repo, member_repo, fake_business):
    pass

def test_update_business_member_call_business_member_repo_update(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member_check_if_business_exist(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member_check_if_user_is_admin_or_owner(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member_raise_exception_if_business_member_dont_exist(business_repo, member_repo, fake_business):
    pass

def test_delete_business_member_raise_exception_if_deleting_owner():
    pass

def test_delete_business_member_raise_exception_if_deleting_self():
    pass

def test_delete_business_member_call_business_member_repo_delete(business_repo, member_repo, fake_business):
    pass


