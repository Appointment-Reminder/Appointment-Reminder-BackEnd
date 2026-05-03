from typing import List, Optional

from fastapi import APIRouter


from app.dependencies import BUSINESS_MEMBER_REPO_DEP, BUSINESS_REPO_DEP, USER_REPOSITORY_DEPENDENCY


from app.dependencies import CURRENT_USER_DEPENDENCY
from app.models.business_member_model import BusinessMemberRead, BusinessMemberInvite, BusinessMemberUpdate
from app.models.business_model import BusinessRead, BusinessCreate, BusinessUpdate
from app.services import business_service


business_router = APIRouter(
    prefix="/business",
    tags=["business"]
)

##TODO CLEAN UP BUSINESS ROUTES

@business_router.post("/businesses", response_model=BusinessRead, status_code=201)
def create_business(
        business_data: BusinessCreate,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Create a new business"""
    return business_service.create_business(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_data=business_data
    )

@business_router.get("/businesses/me", response_model=List[BusinessRead], status_code=200)
def get_all_my_businesses(
        business_repo: BUSINESS_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        is_active: Optional[bool] = None
):
    """Get all businesses the user is part of (owned or member)"""
    return business_service.get_my_businesses(
        business_repo=business_repo,
        current_user=current_user,
        is_active=is_active
    )

@business_router.get("/businesses/{business_id}", response_model=BusinessRead, status_code=200)
def get_specific_business(
        business_id: int,
        business_repo: BUSINESS_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Get a specific business if user is a member"""
    return business_service.get_business_by_id(
        business_repo=business_repo,
        business_id=business_id,
        current_user=current_user
    )

@business_router.put("/businesses/{business_id}", response_model=BusinessRead, status_code=200)
def update_business(
        business_id: int,
        business_data: BusinessUpdate,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Update a business (Owner or admin only)"""
    return business_service.update_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id=business_id,
        business_data=business_data,
        current_user=current_user
    )

@business_router.delete("/businesses/{business_id}", status_code=200)
def delete_business(
        business_id: int,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Delete a business (owner only)"""
    business_service.delete_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id=business_id,
        current_user=current_user
    )
    return None

@business_router.get("/businesses/{business_id}/members", response_model= List[BusinessMemberRead], status_code=200)
def get_business_member_for_business(
        business_id: int,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get all members of a business"""
    return business_service.get_business_member_list(
        business_repo=business_repo,
        member_repo=business_member_repo,
        current_user=current_user,
        business_id=business_id
    )

@business_router.post("/businesses/{business_id/members}", response_model=BusinessMemberRead, status_code=201)
def invite_user_to_join_business(
        business_id: int,
        invite_data: BusinessMemberInvite,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        user_repo: USER_REPOSITORY_DEPENDENCY,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Invite a user to join the business"""
    return business_service.invite_business_member(
        business_repo=business_repo,
        business_member_repo=business_member_repo,
        user_repo=user_repo,
        business_id=business_id,
        invite_data=invite_data,
        current_user=current_user
    )

@business_router.patch("/businesses/{business_id}/members/{member_id}", response_model=BusinessMemberRead, status_code=200)
def update_business_member_role_or_status(
        business_id: int,
        member_id: int,
        member_data: BusinessMemberUpdate,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Update a member's role or active status"""
    return business_service.update_business_member(
        business_repo=business_repo,
        business_member_repo=business_member_repo,
        business_id=business_id,
        member_id=member_id,
        business_member_data=member_data,
        current_user=current_user
    )

@business_router.delete("/businesses/{business_id}/members/{member_id}", status_code=204)
def remove_a_member_from_business(
        business_id: int,
        member_id: int,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Remove a member from the business"""
    business_service.delete_business_member(
        business_repo=business_repo,
        business_member_repo=business_member_repo,
        business_id=business_id,
        business_member_id=member_id,
        current_user=current_user
    )
    return None





'''
@business_router.get("/me", response_model=List[BusinessRead], status_code=200)
def get_my_businesses(
        business_repo: BUSINESS_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY,
        is_active: Optional[bool] = Query(None, description = "Filter by is active business")
):
    """ Get all businesses the user is part of (owned or member)
    Includes the user's role in each business"""
    user_id = current_user.id
    print(f"Logged in owner id {user_id}")

    businesses = business_service.get_business_by_user(business_repo=business_repo, user_id=user_id, is_active=is_active)

    return businesses

@business_router.get("/me/{business_id}", response_model=BusinessRead, status_code=200)
def get_my_business(
    business_id: int,
    business_repo: BUSINESS_REPO_DEP,
    current_user = CURRENT_USER_DEPENDENCY,
):
    """Get a specific business if user is a member"""
    user_id = current_user.id
    business = business_service.get_business_by_id(
        business_repo=business_repo,
        business_id = business_id,
        user_id = user_id
    )

    if not business:
        raise HTTPException(status_code=404, detail="Business not found or you are not a member")

    return business

@business_router.post("/create", response_model=BusinessCreate, status_code=201)
def create_business(
        business_data: BusinessCreate,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Create a new business"""
    created =  business_service.create_business(business_repo= business_repo, member_repo= member_repo, user_id=current_user.id , business_data=business_data)

    if not created:
        raise HTTPException(status_code=403, detail="Business not found or you don t have permission")

    return created

@business_router.put("/me/{business_id}", response_model=BusinessRead, status_code=200)
def update_business(
        business_id: int,
        business: BusinessUpdate,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY
):
    """Update a business (Owner or admin only)"""
    updated = business_service.update_business(
    business_id=business_id,
    user_id = current_user.id,
    business_data=business,
    business_repo=business_repo,
    member_repo=member_repo,
    )

    if not updated:
        raise HTTPException(status_code=403, detail="Business not found or you don t have permission")

    return updated

@business_router.delete("/me/{business_id}", status_code=204)
def delete_business(
        business_id: int,
        business_repo: BUSINESS_REPO_DEP,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY
):
    """Delete a business (owner only)"""
    success = business_service.delete_business(
        business_repo=business_repo,
        member_repo=member_repo,
        business_id = business_id,
        user_id = current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Business not found or you don t have permission"
        )

@business_router.get("{business_id}/members", response_model = List[BusinessMemberRead], status_code=200)
async def get_business_members(
        business_id: int,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY
):
    """Get all members of a business"""
    members = business_service.get_business_member_list(
        business_repo=business_repo,
        member_repo=member_repo,
        current_user=current_user,
        business_id=business_id
    )
    return members


@business_router.post("/{business_id}/members}", response_model=BusinessMemberRead)
async def invite_business_member(
        business_id: int,
        invite_data: BusinessMemberInvite,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        user_repo: USER_REPOSITORY_DEPENDENCY,
        business_repo: BUSINESS_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY):
    """Invite a user to join the business"""
    new_member = business_service.invite_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        user_repo=user_repo,
        business_id=business_id,
        invite_data=invite_data,
        current_user=current_user
    )
    return new_member

@business_router.patch("/{business_id}/members/{member_id}")
async def update_member_role(
        business_id: int,
        member_id: int,
        member_data: BusinessMemberUpdate,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY):
    """Update a member's role or active status"""
    updated_member = business_service.update_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        business_id=business_id,
        member_id=member_id,
        business_member_data=member_data,
        current_user=current_user
    )
    return updated_member

@business_router.delete("/{business_id}/members/{member_id}")
async def remove_member(
        business_id: int,
        member_id: int,
        member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        current_user = CURRENT_USER_DEPENDENCY):
    """Remove a member from the business"""
    business_service.delete_business_member(
        business_repo=business_repo,
        business_member_repo=member_repo,
        business_id=business_id,
        business_member_id=member_id,
        current_user=current_user
    )
    return None

'''