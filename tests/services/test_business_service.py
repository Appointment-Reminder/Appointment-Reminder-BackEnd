from datetime import datetime
from unittest import result
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.sql.functions import current_user

from app.models.business_invitation import BusinessInvitation
from app.models.business_member_model import BusinessMemberInvite, BusinessMemberUpdate
from app.models.business_model import BusinessCreate, BusinessUpdate
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
def user_repo():
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


@pytest.fixture
def fake_owner_member():
    return BusinessMember(
        id=1,
        business_id=1,
        user_id=42,
        role=MemberRole.OWNER,
        is_active=True,
        joined_at=datetime.utcnow()
    )


@pytest.fixture
def fake_admin_member():
    return BusinessMember(
        id=2,
        business_id=1,
        user_id=43,
        role=MemberRole.ADMIN,
        is_active=True,
        joined_at=datetime.utcnow()
    )


@pytest.fixture
def fake_regular_member():
    return BusinessMember(
        id=3,
        business_id=1,
        user_id=44,
        role=MemberRole.PHOTOGRAPHER,
        is_active=True,
        joined_at=datetime.utcnow()
    )


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

def test_get_my_business_calls_find_by_user(business_repo, member_repo, fake_business):
    business_repo.find_by_user.return_value = fake_business
    current_user = User(id=42, name="Test")
    result = business_service.get_my_businesses(business_repo, current_user=current_user, is_active=True)
    business_repo.find_by_user.assert_called_once()
    assert result == fake_business

def test_get_my_business_without_business(business_repo, member_repo, fake_business):
    business_repo.find_by_user.return_value = None
    current_user = User(id=42, name="Test")
    with pytest.raises(HTTPException) as exc_info:
        result = business_service.get_my_businesses(business_repo, current_user=current_user, is_active=True)

    assert exc_info.value.status_code == 404

def test_get_business_by_id(business_repo, member_repo, fake_business):
    business_repo.find_by_id_and_user.return_value = fake_business
    current_user = User(id=42, name="Test")
    result = business_service.get_business_by_id(business_repo, business_id=1, current_user=current_user)
    assert result == fake_business

def test_get_business_by_id_without_business(business_repo, member_repo, fake_business):
    business_repo.find_by_id_and_user.return_value = None
    current_user = User(id=42, name="Test")
    with pytest.raises(HTTPException) as exc_info:
        result = business_service.get_business_by_id(business_repo, business_id=1, current_user=current_user)
    assert exc_info.value.status_code == 404

def test_get_business_by_id_chek_if_business_exist(business_repo, member_repo, fake_business):
    business_repo.find_by_id_and_user.return_value = fake_business
    current_user = User(id=42, name="Test")
    result = business_service.get_business_by_id(business_repo, business_id=1, current_user=current_user)
    business_repo.find_by_id_and_user.assert_called_once()

def test_update_business(business_repo, member_repo, fake_business):
    updated_business = Business(name="Updated", owner_id=1)
    updated_business.id = 1
    business_repo.update.return_value = updated_business
    business_data = BusinessUpdate(name="Updated")
    current_user = User(id=42, name="Test")
    with patch("app.services.business_service.check_if_business_exist", return_value=True):
        with patch("app.services.business_service.check_user_is_admin_or_owner_for_business", return_value=True):
            result = business_service.update_business(business_repo, member_repo=member_repo,business_id=1, business_data=business_data, current_user=current_user)
    business_repo.update.assert_called_once()
    business_repo.update.assert_called_once_with(business_id=1, business_data=business_data)
    assert result.name == "Updated"


def test_update_business_call_check_business_exist(business_repo, member_repo, fake_business):
    """Test that update_business checks if business exists"""
    business_repo.find_by_id.return_value = None
    current_user = User(id=42, name="Test")
    business_data = BusinessUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business(
            business_repo=business_repo,
            member_repo=member_repo,
            business_id=1,
            current_user=current_user,
            business_data=business_data
        )

    assert exc_info.value.status_code == 404
    business_repo.find_by_id.assert_called_once_with(1)


def test_update_business_call_check_is_user_admin_or_owner(business_repo, member_repo, fake_business,
                                                           fake_regular_member):
    """Test that update_business verifies user is admin or owner"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_regular_member

    current_user = User(id=44, name="Regular User")
    business_data = BusinessUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business(
            business_repo=business_repo,
            member_repo=member_repo,
            business_id=1,
            current_user=current_user,
            business_data=business_data
        )

    assert exc_info.value.status_code == 403
    assert "Only business owners and admins" in exc_info.value.detail


def test_delete_all_members_for_business_id_call_is_user_admin_or_owner(member_repo, fake_regular_member):
    """Test that delete_all_members verifies user permissions"""
    member_repo.get_member.return_value = fake_regular_member
    current_user = User(id=44, name="Regular User")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_all_members_for_business_id(
            member_repo=member_repo,
            business_id=1,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403

## DELETE TEST
def test_delete_business(business_repo, member_repo, fake_business, fake_owner_member):
    """Test successful business deletion"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_owner_member
    member_repo.get_by_business_id.return_value = [fake_owner_member]
    business_repo.delete.return_value = True

    current_user = User(id=42, name="Test")

    result = business_service.delete_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id=1,
        current_user=current_user
    )

    assert result is True
    business_repo.delete.assert_called_once_with(1)


def test_delete_business_call_check_business_exist(business_repo, member_repo):
    """Test that delete_business checks if business exists"""
    business_repo.find_by_id.return_value = None
    current_user = User(id=42, name="Test")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business(
            business_repo=business_repo,
            member_repo=member_repo,
            business_id=1,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404


def test_delete_business_call_is_user_admin_or_owner(business_repo, member_repo, fake_business, fake_regular_member):
    """Test that delete_business verifies user permissions"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_regular_member
    current_user = User(id=44, name="Regular User")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business(
            business_repo=business_repo,
            member_repo=member_repo,
            business_id=1,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403


def test_delete_busines_call_delete_all_business_members_for_business_id(business_repo, member_repo, fake_business,
                                                                         fake_owner_member):
    """Test that delete_business deletes all members first"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_owner_member
    member_repo.get_by_business_id.return_value = [fake_owner_member]
    business_repo.delete.return_value = True

    current_user = User(id=42, name="Test")

    business_service.delete_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id=1,
        current_user=current_user
    )

    member_repo.get_by_business_id.assert_called_once_with(1)
    member_repo.delete.assert_called()


def test_delete_business_call_business_repo_delete(business_repo, member_repo, fake_business, fake_owner_member):
    """Test that delete_business calls repository delete method"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_owner_member
    member_repo.get_by_business_id.return_value = []
    business_repo.delete.return_value = True

    current_user = User(id=42, name="Test")

    business_service.delete_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id=1,
        current_user=current_user
    )

    business_repo.delete.assert_called_once_with(1)


##TEST IF BUSINESS EXIST
def test_if_business_exist_return_true_if_business_exist_for_user(business_repo, fake_business):
    """Test that check_if_business_exist doesn't raise exception for existing business"""
    business_repo.find_by_id.return_value = fake_business

    # Should not raise an exception
    business_service.check_if_business_exist(business_id=1, business_repo=business_repo)

    business_repo.find_by_id.assert_called_once_with(1)


def test_if_business_exist_raise_exception_if_business_dont_exist_for_user(business_repo):
    """Test that check_if_business_exist raises exception for non-existent business"""
    business_repo.find_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        business_service.check_if_business_exist(business_id=1, business_repo=business_repo)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Business not found"

#check user is admin
def test_check_if_user_is_admin_or_owner_raise_exception_if_user_is_not_admin_or_owner(member_repo,
                                                                                       fake_regular_member):
    """Test that check raises exception when user is not admin or owner"""
    member_repo.get_member.return_value = fake_regular_member
    current_user = User(id=44, name="Regular User")

    with pytest.raises(HTTPException) as exc_info:
        business_service.check_user_is_admin_or_owner_for_business(
            business_id=1,
            business_member_repo=member_repo,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Only business owners and admins" in exc_info.value.detail


def test_check_if_user_is_admin_or_owner_dont_raise_exception_if_user_is_admin_or_owner(member_repo, fake_owner_member):
    """Test that check doesn't raise exception when user is admin or owner"""
    member_repo.get_member.return_value = fake_owner_member
    current_user = User(id=42, name="Owner User")

    # Should not raise an exception
    business_service.check_user_is_admin_or_owner_for_business(
        business_id=1,
        business_member_repo=member_repo,
        current_user=current_user
    )

    member_repo.get_member.assert_called_once_with(business_id=1, user_id=42)

#INVITE BUSINESS MEMBER
def test_invite_business_member(business_repo, member_repo, user_repo, fake_business, fake_owner_member):
    """Test successful business member invitation"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.side_effect = [fake_owner_member, None]  # Current user is owner, invited user not a member

    invited_user = User(id=50, name="Invited User", email="invited@example.com")
    user_repo.get_by_email.return_value = invited_user

    new_member = BusinessMember(
        id=5,
        business_id=1,
        user_id=50,
        role=MemberRole.PHOTOGRAPHER,
        invited_by=42
    )
    member_repo.create.return_value = new_member

    current_user = User(id=42, name="Owner")
    invite_data = BusinessMemberInvite(user_email="invited@example.com", role=MemberRole.PHOTOGRAPHER)

    result = business_service.invite_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        user_repo=user_repo,
        business_id=1,
        invite_data=invite_data,
        current_user=current_user
    )

    user_repo.get_by_email.assert_called_once_with("invited@example.com")
    member_repo.create.assert_called_once()
    assert result.user_id == 50

# GET BUSINESS MEMBER LIST
def test_get_business_member_list_check_if_business_exist_for_user(business_repo, member_repo):
    """Test that get_business_member_list checks if business exists"""
    business_repo.find_by_id.return_value = None
    current_user = User(id=42, name="Test")

    with pytest.raises(HTTPException) as exc_info:
        business_service.get_business_member_list(
            business_repo=business_repo,
            member_repo=member_repo,
            current_user=current_user,
            business_id=1
        )

    assert exc_info.value.status_code == 404


def test_get_business_member_list_return_member_list(business_repo, member_repo, fake_business, fake_owner_member,
                                                     fake_admin_member):
    """Test successful retrieval of business member list"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_owner_member
    member_repo.get_by_business_id.return_value = [fake_owner_member, fake_admin_member]

    current_user = User(id=42, name="Test")

    result = business_service.get_business_member_list(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_id=1
    )

    assert len(result) == 2
    member_repo.get_by_business_id.assert_called_once_with(1)


def test_get_business_member_list_return_empty_list_if_no_member(business_repo, member_repo, fake_business,
                                                                 fake_owner_member):
    """Test that empty list is returned when business has no members"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_owner_member
    member_repo.get_by_business_id.return_value = []

    current_user = User(id=42, name="Test")

    result = business_service.get_business_member_list(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_id=1
    )

    assert result == []

# update business member
def test_update_business_member_check_if_business_exist(business_repo, member_repo):
    """Test that update_business_member checks if business exists"""
    business_repo.find_by_id.return_value = None
    current_user = User(id=42, name="Test")
    update_data = BusinessMemberUpdate(role=MemberRole.ADMIN, is_active=True)

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            member_id=2,
            business_member_data=update_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404


def test_update_business_member_check_if_user_is_admin_or_owner(business_repo, member_repo, fake_business,
                                                                fake_regular_member):
    """Test that update_business_member verifies user permissions"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_regular_member

    current_user = User(id=44, name="Regular User")
    update_data = BusinessMemberUpdate(role=MemberRole.ADMIN, is_active=True)

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            member_id=2,
            business_member_data=update_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403


def test_update_business_member_raise_exception_if_user_update_to_owner_by_admin(
        business_repo, member_repo, fake_business, fake_admin_member, fake_regular_member
):
    """Test that admin cannot promote member to owner"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.side_effect = [fake_admin_member, fake_admin_member, fake_regular_member]

    current_user = User(id=43, name="Admin User")
    update_data = BusinessMemberUpdate(role=MemberRole.OWNER, is_active=True)

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            member_id=44,
            business_member_data=update_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403
    assert "Only owners can assign owner role" in exc_info.value.detail


def test_update_business_member_raise_exception_if_change_owner_role(
        business_repo, member_repo, fake_business
):
    """Test that owner role cannot be changed"""
    business_repo.find_by_id.return_value = fake_business

    current_member = BusinessMember(id=2, business_id=1, user_id=43, role=MemberRole.OWNER)
    target_member = BusinessMember(id=1, business_id=1, user_id=42, role=MemberRole.OWNER)

    member_repo.get_member.side_effect = [current_member, current_member, target_member]

    current_user = User(id=43, name="Owner User")
    update_data = BusinessMemberUpdate(role=MemberRole.ADMIN, is_active=True)

    with pytest.raises(HTTPException) as exc_info:
        business_service.update_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            member_id=42,
            business_member_data=update_data,
            current_user=current_user
        )

    assert exc_info.value.status_code == 400
    assert "Cannot change owner role" in exc_info.value.detail


def test_update_business_member_call_business_member_repo_update(
        business_repo, member_repo, fake_business, fake_owner_member, fake_regular_member
):
    """Test that update_business_member calls repository update method"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.side_effect = [fake_owner_member, fake_owner_member, fake_regular_member]

    updated_member = BusinessMember(
        id=3,
        business_id=1,
        user_id=44,
        role=MemberRole.ADMIN,
        is_active=True
    )
    member_repo.update.return_value = updated_member

    current_user = User(id=42, name="Owner")
    update_data = BusinessMemberUpdate(role=MemberRole.ADMIN, is_active=True)

    result = business_service.update_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        business_id=1,
        member_id=44,
        business_member_data=update_data,
        current_user=current_user
    )

    member_repo.update.assert_called_once()
    assert result.role == MemberRole.ADMIN


# Delete business member
def test_delete_business_member_check_if_business_exist(business_repo, member_repo):
    """Test that delete_business_member checks if business exists"""
    business_repo.find_by_id.return_value = None
    current_user = User(id=42, name="Test")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            business_member_id=2,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404


def test_delete_business_member_check_if_user_is_admin_or_owner(
        business_repo, member_repo, fake_business, fake_regular_member
):
    """Test that delete_business_member verifies user permissions"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.return_value = fake_regular_member

    current_user = User(id=44, name="Regular User")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            business_member_id=2,
            current_user=current_user
        )

    assert exc_info.value.status_code == 403


def test_delete_business_member_raise_exception_if_business_member_dont_exist(
        business_repo, member_repo, fake_business, fake_owner_member
):
    """Test that exception is raised when member doesn't exist"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.side_effect = [fake_owner_member, None]

    current_user = User(id=42, name="Owner")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            business_member_id=999,
            current_user=current_user
        )

    assert exc_info.value.status_code == 404
    assert "Member not found" in exc_info.value.detail


def test_delete_business_member_raise_exception_if_deleting_owner(
        business_repo, member_repo, fake_business
):
    """Test that owner cannot be deleted"""
    business_repo.find_by_id.return_value = fake_business

    owner_as_current = BusinessMember(id=2, business_id=1, user_id=43, role=MemberRole.OWNER)
    owner_to_delete = BusinessMember(id=1, business_id=1, user_id=42, role=MemberRole.OWNER)

    member_repo.get_member.side_effect = [owner_as_current, owner_to_delete]

    current_user = User(id=43, name="Another Owner")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            business_member_id=42,
            current_user=current_user
        )

    assert exc_info.value.status_code == 400
    assert "Cannot remove business owner" in exc_info.value.detail


def test_delete_business_member_raise_exception_if_deleting_self(
        business_repo, member_repo, fake_business, fake_admin_member
):
    """Test that user cannot delete themselves"""
    business_repo.find_by_id.return_value = fake_business

    # Current user is admin trying to delete themselves
    member_repo.get_member.side_effect = [fake_admin_member, fake_admin_member]

    current_user = User(id=43, name="Admin User")

    with pytest.raises(HTTPException) as exc_info:
        business_service.delete_business_member(
            business_repo=business_repo,
            business_member_repo=member_repo,
            business_id=1,
            business_member_id=43,
            current_user=current_user
        )

    assert exc_info.value.status_code == 400
    assert "Cannot remove yourself" in exc_info.value.detail


def test_delete_business_member_call_business_member_repo_delete(
        business_repo, member_repo, fake_business, fake_owner_member, fake_regular_member
):
    """Test that delete_business_member calls repository delete method"""
    business_repo.find_by_id.return_value = fake_business
    member_repo.get_member.side_effect = [fake_owner_member, fake_regular_member]

    current_user = User(id=42, name="Owner")

    business_service.delete_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        business_id=1,
        business_member_id=44,
        current_user=current_user
    )

    member_repo.delete.assert_called_once_with(1)



