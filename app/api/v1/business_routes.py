from typing import List, Optional

from fastapi import APIRouter


from app.dependencies import BUSINESS_MEMBER_REPO_DEP, BUSINESS_REPO_DEP, USER_REPOSITORY_DEPENDENCY


from app.dependencies import CURRENT_USER_DEPENDENCY
from app.models.Member.business_member_commissions import BusinessMemberCommissionsCreate, BusinessMemberCommissionsRead
from app.models.Member.busioness_member_form_model import BusinessMemberFormRead, BusinessMemberFormCreate, \
    BusinessMemberFormUpdate
from app.models.business_member_model import BusinessMemberRead, BusinessMemberInvite, BusinessMemberUpdate
from app.models.business_model import BusinessRead, BusinessCreate, BusinessUpdate
from app.models.package.package_alias_model import PackageAliasCreate, PackageAliasRead
from app.models.package.package_category_model import PackageCategoryRead, PackageCategoryCreate
from app.models.package.package_model import PackageCreate, PackageRead, PackageUpdate
from app.models.package.package_price_model import PackagePriceRead, PackagePriceCreate
from app.services import business_service
from models.package.package_price import PackagePrice

business_router = APIRouter(
    prefix="/business",
    tags=["business"]
)

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

@business_router.post("/businesses/{business_id}/invite", response_model=BusinessMemberRead, status_code=201)
def invite_user_to_join_business(
        business_id: int,
        invite_data: BusinessMemberInvite,
        business_member_repo: BUSINESS_MEMBER_REPO_DEP,
        business_repo: BUSINESS_REPO_DEP,
        user_repo: USER_REPOSITORY_DEPENDENCY,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Invite a user to join the business"""
    print('Receive invite member')
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

##Category
@business_router.post("/categories", status_code=201, response_model=PackageCategoryRead)
def create_package_category(package_category: PackageCategoryCreate):
    """Create a new package category for business owner and admin"""
    pass

@business_router.get("/{business_id}/categories",response_model=List[PackageCategoryRead], status_code=200)
def get_package_categories_for_business(
        business_id: int,
):
    """Get the list of all package categories for business"""
    pass

@business_router.delete("/categories/{category_id}", status_code=204)
def delete_package_category(business_id: int, category_id: int):
    """Delete a package category for business, owner and admin only"""
    pass

##Package
@business_router.post("/packages", response_model=PackageRead, status_code=201)
def create_package(package: PackageCreate):
    """Create a new package for business, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/packages", response_model=List[PackageRead], status_code=200)
def get_packages_for_business(business_id: int):
    """Get the list of all packages for business"""
    pass

@business_router.get("/packages/{package_id}", response_model=PackageRead, status_code=200)
def get_package(package_id: int):
    """Get a package for business, for business_member_ only"""
    pass

@business_router.put("/packages", response_model=PackageRead)
def update_package(package: PackageUpdate):
    """Update a package for business, for admin and owner only"""
    pass

@business_router.delete("/packages/{package_id}", status_code=200)
def delete_package(package_id: int):
    """Delete a package for business, for admin and owner only"""
    pass

##package price route
@business_router.post("/businesses/{business_id}/packages/{package_id}/prices}", status_code=201, response_model=PackagePriceRead)
def create_price(price: PackagePriceCreate, business_id:int, package_id:int):
    """Create a new package for business and package, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/packages/{package_id}/prices", status_code=200, response_model=List[PackagePrice])
def get_prices_history(business_id:int, package_id:int):
    """Get the history of package prices for business, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/packages/{package_id}/prices/current", response_model=PackagePriceRead, status_code=200)
def get_current_price_of_package(business_id:int, package_id:int):
    """Get the current price of package, owner and admin only"""
    pass


## BusinessMemberForm
@business_router.post("/businesses/{business_id}/members/{member_id}/forms", status_code=201, response_model=BusinessMemberFormRead)
def create_business_member_form(member: BusinessMemberFormCreate, business_id:int, package_id:int):
    """Create a new business member form for business, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/members/{member_id}/forms", status_code=200, response_model=List[BusinessMemberFormRead])
def get_business_member_forms(business_id:int, member_id:int):
    """Get the business member forms for business, owner and admin only"""
    pass

@business_router.patch("/businesses/{business_id}/members/{member_id}/forms", status_code=200, response_model=BusinessMemberFormRead)
def update_business_member_form(business_id:int, member_id:int, form: BusinessMemberFormUpdate):
    """Update a business member form for business, owner and admin only"""
    pass

@business_router.delete("/businesses/{business_id}/members/{member_id}/forms/{form_id}", status_code=204)
def delete_business_member_form(business_id:int, member_id:int, form_id:int):
    """Delete a business member form for business, owner and admin only"""
    pass

#member commission route
@business_router.post("/businesses/{business_id}/members/{member_id}/commissions", response_model=BusinessMemberCommissionsRead, status_code=201)
def create_member_commission(business_id, member_id:int, commissions:BusinessMemberCommissionsCreate):
    """Create a new member commission for business, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/members/{member_id}/commissions", response_model=List[BusinessMemberCommissionsRead], status_code=200)
def get_member_commissions(business_id:int, member_id:int):
    """Get the commissions for business, owner and admin only"""
    pass

@business_router.get("/businesses/{business_id}/members/{member_id}/{package_id}/commissions", response_model=BusinessMemberCommissionsRead, status_code=200)
def get_member_current_commission_on_package(business_id:int, member_id:int, package_id:int):
    """Get the current commission for package, owner and admin only"""
    pass


