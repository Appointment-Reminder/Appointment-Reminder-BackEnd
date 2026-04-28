from datetime import datetime
from typing import Optional, List, Any

from sqlmodel import Session, select

from app.db.models.business import Business
from app.db.models.business_member import MemberRole, BusinessMember
from app.models.business_model import BusinessCreate
from app.repositories import business_member_repository
from app.repositories.business_repository import BusinessRepository

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

def create_business(business_repo: BusinessRepository, member_repo: business_member_repository, user_id: int, business_data: BusinessCreate) -> Business:
    """ Create a business for the current user"""

    if business_repo.find_by_name(user_id, business_data.name):
        raise Exception("business already exists")

    business = Business(**business_data.dict(), owner_id=user_id)
    saved = business_repo.create(business)

    member = BusinessMember(
        business_id=saved.id,
        user_id=user_id,
        role=MemberRole.OWNER,
        joined_at=datetime.utcnow(),
    )

    member_repo.create(member)
    return saved

def get_business_by_user(
        business_repo: BusinessRepository,
        user_id: int,
        is_active: Optional[bool] = True
) -> List[dict]:
    """ Get All Businesses a user is part of (owner or member) return list with business info + user's role"""
    results = business_repo.find_by_user(user_id, is_active)
    return [_to_dict(business, role) for business, role in results]

def get_business_by_id(business_repo: BusinessRepository, business_id: int, user_id: int) -> dict[str, Any] | None:
    """  Get a specific business if user is a member (not just owner)
    Returns business + user's role"""
    result = business_repo.find_by_id_and_user(business_id, user_id)
    if not result:
        raise Exception("Business not found or you are not a member")
    business, role = result
    return _to_dict(business, role)

def update_business(business_repo: BusinessRepository, member_repo: business_member_repository, business_id: int, user_id: int, business_data: Business) -> Optional[Business]:
    """Update a business (only owner or admin can update)"""
    if not member_repo.is_owner_or_admin(business_id, user_id):
        raise PermissionError("You don't have permission to update this business")

    business = business_repo.find_by_id(business_id)
    if not business:
        raise Exception("Business not found")

    return business_repo.update(business, business_data)

def delete_business(business_repo: BusinessRepository, member_repo: business_member_repository, business_id: int, user_id: int) -> bool:
    business = business_repo.find_by_id(business_id)
    if not business or business.owner_id != user_id:
        raise PermissionError("Business not found or you don't have permission")

    business_repo.delete(business)




