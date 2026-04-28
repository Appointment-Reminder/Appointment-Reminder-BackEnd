from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session

from app.dependencies import BUSINESS_MEMBER_REPO_DEP, BUSINESS_REPO_DEP, CURRENT_USER_DEPENDENCY

from app.db.session import get_session
from app.dependencies import CURRENT_USER_DEPENDENCY
from app.models.business_model import BusinessRead, BusinessCreate, BusinessUpdate
from app.repositories.business_repository import BusinessRepository
from app.services import business_service


business_router = APIRouter(
    prefix="/business",
    tags=["business"]
)

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
        current_user = CURRENT_USER_DEPENDENCY
):
    """Create a new business"""
    created =  business_service.create_business(business_repo, member_repo, current_user.id, business_data)

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
