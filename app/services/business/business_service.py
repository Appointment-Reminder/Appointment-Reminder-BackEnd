from datetime import datetime
from typing import Optional, List, Any

from fastapi import HTTPException

from app.db.models.business import Business
from app.db.models.business_member import MemberRole, BusinessMember
from app.models.business_member_model import BusinessMemberUpdate, BusinessMemberInvite
from app.models.business_model import BusinessCreate, BusinessUpdate
from app.repositories import business_member_repository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository
from app.db.models.user import User
from app.services.business.BusinessGuard import BusinessGuard
from app.services.errors.BusinessErrors import MemberRemoval, OwnerRoleEditing, InvalidBusinessAuthorization, \
    UserNotFoundInBusiness, UserAlreadyMemberOfBusiness, InvalidBusiness, BusinessAlreadyExists
from app.services.errors.user_errors import UserNotFound


def _to_dict(business: Business, role: str) -> dict[str, Any]:
    return {
        "id": business.id,
        "name": business.name,
        "description": business.description,
        "owner_id": business.owner_id,
        "is_active": business.is_active,
        "created_at": business.created_at,
        "updated_at": business.updated_at,
        "my_role": role,
    }

def create_business(business_repo: BusinessRepository, member_repo: BusinessMemberRepository, current_user: User, business_data: BusinessCreate) -> Business:
    """ Create a business for the current user"""

    if business_repo.find_by_name(business_data.name):
        raise BusinessAlreadyExists(business_name=business_data.name)

    business = Business(
        name=business_data.name,
        description=business_data.description,
        owner_id=current_user.id,  # Pass the actual integer value
        is_active=True,
    )
    saved = business_repo.create(business)

    member = BusinessMember(
        business_id=saved.id,
        user_id=current_user.id,
        role=MemberRole.OWNER,
        joined_at=datetime.now(),
    )

    member_repo.create(member)
    return saved

def get_my_businesses(business_repo: BusinessRepository, current_user: User, is_active: Optional[bool]) -> list[Business]:
    result = business_repo.find_by_user(current_user.id, is_active)

    if not result:
        raise InvalidBusiness(business_id=0)
    return result

def get_business_by_id(business_repo: BusinessRepository, business_id: int, current_user: User) -> Business | None:
    """  Get a specific business if user is a member (not just owner)
    Returns business + user's role"""
    check_if_business_exist(business_id=business_id, business_repo=business_repo)

    result = business_repo.find_by_id_and_user(business_id, current_user.id)
    if not result:
        raise InvalidBusiness(business_id)
    return result

def update_business(business_repo: BusinessRepository, member_repo: BusinessMemberRepository, business_id: int, current_user: User, business_data: BusinessUpdate) -> Optional[Business]:
    """Update a business (only owner or admin can update)"""
    check_if_business_exist(business_id=business_id, business_repo=business_repo)
    check_user_is_admin_or_owner_for_business(business_id=business_id,business_member_repo=member_repo, current_user=current_user)

    return business_repo.update(business_id = business_id, business_data= business_data)

def delete_all_members_for_business_id(member_repo: BusinessMemberRepository, business_id: int, current_user: User) -> None:
    """Delete all members of a business"""
    check_user_is_admin_or_owner_for_business(business_id=business_id, business_member_repo=member_repo, current_user=current_user)
    members = member_repo.get_by_business_id(business_id)

    for member in members:
        member_repo.delete(member.id)

def delete_business(business_repo: BusinessRepository, member_repo: BusinessMemberRepository, business_id: int, current_user: User) -> bool:
    check_if_business_exist(business_id=business_id, business_repo=business_repo)
    check_user_is_admin_or_owner_for_business(business_id=business_id,business_member_repo=member_repo, current_user=current_user)
    delete_all_members_for_business_id(member_repo=member_repo, business_id=business_id, current_user=current_user)
    return business_repo.delete(business_id)

def check_if_business_exist(business_id: int, business_repo: BusinessRepository):
    business = business_repo.find_by_id(business_id)
    if not business:
        raise InvalidBusiness(business_id)

def check_user_is_admin_or_owner_for_business(business_id: int, business_member_repo: BusinessMemberRepository,
                                              current_user: User):
    current_member = business_member_repo.get_member(
        business_id=business_id,
        user_id=current_user.id)
    if not current_member or current_member.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise InvalidBusinessAuthorization(business_id)

def invite_business_member(
        business_repo: BusinessRepository,
        business_member_repo: BusinessMemberRepository,
        user_repo,  # Add UserRepository
        business_id: int,
        invite_data: BusinessMemberInvite,
        current_user: User
) -> BusinessMember:
    """Invite a user to join a business"""

    check_if_business_exist(business_id=business_id, business_repo=business_repo)
    check_user_is_admin_or_owner_for_business(business_id, business_member_repo, current_user)

    invited_user = user_repo.get_by_email(invite_data.user_email)
    if not invited_user:
        raise UserNotFound(invite_data.user_email)

    existing_member = business_member_repo.get_member(business_id=business_id, user_id=invited_user.id)
    if existing_member:
        raise UserAlreadyMemberOfBusiness(existing_member.user_id)

    # Create new member
    new_member = BusinessMember(
        business_id=business_id,
        user_id=invited_user.id,
        role=invite_data.role,
        invited_by=current_user.id
    )

    created_member = business_member_repo.create(new_member)

    # TODO: Send invitation email

    return created_member



def get_business_member_list(
        business_repo: BusinessRepository,
        member_repo: BusinessMemberRepository,  # Fix: business_member_repository
        current_user: User,
        business_id: int
) -> List[BusinessMember]:  # Add return type

    check_if_business_exist(business_id, business_repo)

    current_member = member_repo.get_member(business_id=business_id, user_id=current_user.id)
    if not current_member:
        raise InvalidBusinessAuthorization(business_id)

    members = member_repo.get_by_business_id(business_id)
    return members

def update_business_member(
        business_repo: BusinessRepository,
        business_member_repo: BusinessMemberRepository,
        business_id: int,  # Add this
        member_id: int,    # Add this
        business_member_data: BusinessMemberUpdate,  # Use Update schema, not Create
        current_user: User
) -> BusinessMember:

    check_if_business_exist(business_id=business_id, business_repo=business_repo)
    check_user_is_admin_or_owner_for_business(business_id, business_member_repo, current_user)

    current_member = business_member_repo.get_member(
        business_id=business_id,
        user_id=current_user.id
    )

    print(f'Try to get the business member for user is {member_id} business id {business_id}')
    # Get member to update
    member = business_member_repo.get_member_by_id( member_id=member_id)
    print(f"found member {member}")
    if not member:
        raise UserNotFoundInBusiness(current_user.id, business_id)

    # Prevent changing owner role
    if member.role == MemberRole.OWNER and business_member_data.role != MemberRole.OWNER:
        raise OwnerRoleEditing(current_user.id, business_id) ()

    # Prevent non-owners from creating new owners
    if (business_member_data.role == MemberRole.OWNER and
            current_member.role != MemberRole.OWNER):
        raise OwnerRoleEditing(current_user.id, business_id)

    # Update fields
    if business_member_data.role is not None:
        member.role = business_member_data.role
    if business_member_data.is_active is not None:
        member.is_active = business_member_data.is_active

    updated_member = business_member_repo.update(member)
    return updated_member

def delete_business_member(
        business_repo: BusinessRepository,
        business_member_repo: BusinessMemberRepository,
        business_id: int,  # Add this
        business_member_id: int,
        current_user: User
) -> None:

    check_if_business_exist(business_id, business_repo)
    check_user_is_admin_or_owner_for_business(business_id, business_member_repo, current_user)

    # Get member to delete
    member = business_member_repo.get_member(business_id=business_id, user_id=business_member_id)
    if not member or member.business_id != business_id:
        raise InvalidBusinessAuthorization(business_id)

    # Prevent deleting owner
    if member.role == MemberRole.OWNER:
        raise OwnerRoleEditing(current_user.id, member.business_id)

    # Prevent self-deletion (optional - you might want to allow this)
    if member.user_id == current_user.id:
        raise MemberRemoval(current_user.id, member.user_id, member.business_id)

    business_member_repo.delete(member.business_id)



