from typing import List, Optional

from fastapi import APIRouter
from sqlalchemy.sql.functions import current_user

from app.dependencies import BUSINESS_MEMBER_REPO_DEP, BUSINESS_REPO_DEP, USER_REPOSITORY_DEPENDENCY, \
    BUSINESS_SERVICE_DEP, PACKAGE_SERVICE_DEP

from app.dependencies import CURRENT_USER_DEPENDENCY
from app.models.Member.business_member_commissions import BusinessMemberCommissionsCreate, \
    BusinessMemberCommissionsRead, BusinessMemberCommissionsUpdate
from app.models.Member.busioness_member_form_model import BusinessMemberFormRead, BusinessMemberFormCreate, \
    BusinessMemberFormUpdate
from app.models.business_member_model import BusinessMemberRead, BusinessMemberInvite, BusinessMemberUpdate
from app.models.business_model import BusinessRead, BusinessCreate, BusinessUpdate
from app.models.package.package_category_model import PackageCategoryRead, PackageCategoryCreate, PackageCategoryUpdate
from app.models.package.package_model import PackageCreate, PackageRead, PackageUpdate
from app.models.package.package_price_model import PackagePriceRead, PackagePriceCreate

business_router = APIRouter(
    prefix="/business",
)

@business_router.post("/", response_model=BusinessRead, status_code=201, tags=["business"])
def create_business(
        data: BusinessCreate,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Create a new business"""
    return service.create(data=data, current_user=current_user)

@business_router.get("/me", response_model=List[BusinessRead], status_code=200, tags=["business"])
def get_all_my_businesses(
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
        is_active: Optional[bool] = None
):
    """Get all businesses the user is part of (owned or member)"""
    return service.get_for_user(current_user=current_user, is_active=is_active, business_id=None)

@business_router.get("/{business_id}", response_model=BusinessRead, status_code=200, tags=["business"])
def get_specific_business(
        business_id: int,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Get a specific business if user is a member"""
    return service.get_for_user(current_user=current_user, business_id=business_id, is_active=None)

@business_router.put("/{business_id}", response_model=BusinessRead, status_code=200, tags=["business"])
def update_business(
        business_id: int,
        data: BusinessUpdate,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Update a business (Owner or admin only)"""
    return service.update(business_id=business_id, data=data, current_user=current_user)

@business_router.delete("/{business_id}", status_code=200, tags=["business"])
def delete_business(
        business_id: int,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Delete a business (owner only)"""
    service.delete(business_id=business_id, current_user=current_user)
    return None

@business_router.get("/{business_id}/members", response_model= List[BusinessMemberRead], status_code=200, tags=["business - members"])
def get_business_member_for_business(
        business_id: int,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get all members of a business"""
    return service.get_members(business_id=business_id, current_user=current_user)

@business_router.post("/{business_id}/invite", response_model=BusinessMemberRead, status_code=201, tags=["business - members"])
def invite_user_to_join_business(
        business_id: int,
        invite_data: BusinessMemberInvite,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Invite a user to join the business"""
    print('Receive invite member')
    return service.invite_member(business_id=business_id, invite_data=invite_data, current_user=current_user)


@business_router.patch("/{business_id}/members/{member_id}", response_model=BusinessMemberRead, status_code=200, tags=["business - members"])
def update_business_member_role_or_status(
        business_id: int,
        member_id: int,
        member_data: BusinessMemberUpdate,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Update a member's role or active status"""
    return service.update_member(data=member_data, member_id=member_id, business_id=business_id, current_user=current_user)

@business_router.delete("/{business_id}/members/{member_id}", status_code=204, tags=["business - members"])
def remove_a_member_from_business(
        business_id: int,
        member_id: int,
        service: BUSINESS_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Remove a member from the business"""
    service.delete_member(business_id=business_id, member_id=member_id, current_user=current_user)
    return None



##Package
@business_router.post("/packages", response_model=PackageRead, status_code=201, tags=["business - package"])
def create_package(
        package: PackageCreate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Create a new package for business, owner and admin only"""
    return service.create(data=package, current_user=current_user)

@business_router.get("/{business_id}/packages", response_model=List[PackageRead], status_code=200, tags=["business - package"])
def get_packages_for_business(
        business_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
):
    """Get the list of all packages for business"""
    return service.list(business_id=business_id, current_user=current_user)

@business_router.get("/packages/{package_id}", response_model=PackageRead, status_code=200, tags=["business - package"])
def get_package(
        package_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
):
    """Get a package for business, for business_member_ only"""
    return service.get(package_id=package_id, current_user=current_user)

@business_router.put("/packages", response_model=PackageRead, tags=["business - package"])
def update_package(
        package: PackageUpdate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY,
):
    """Update a package for business, for admin and owner only"""
    return service.update(data=package, current_user=current_user)

@business_router.delete("/packages/{package_id}", status_code=200, tags=["business - package"])
def delete_package(
        package_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Delete a package for business, for admin and owner only"""
    return service.delete(package_id=package_id, current_user=current_user)


##package price route
@business_router.post("/packages/prices", status_code=201, response_model=PackagePriceRead, tags=["business - package - price"])
def create_price(
        price: PackagePriceCreate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
       ):
    """Create a new package for business and package, owner and admin only"""
    return service.create_price(data=price, current_user=current_user)



@business_router.get("/packages/{package_id}/prices", status_code=200, response_model=List[PackagePriceRead], tags=["business - package - price"])
def get_prices_history(
        package_id:int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Get the history of package prices for business, owner and admin only"""
    return service.get_price(package_id=package_id, current_user=current_user, is_current=False, is_personal=None)

@business_router.get("/packages/{package_id}/prices/current", response_model=PackagePriceRead, status_code=200, tags=["business - package - price"])
def get_current_price_of_package(
        package_id:int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Get the current price of package, owner and admin only"""
    return service.get_price(package_id=package_id, current_user=current_user, is_current=True, is_personal=None)

@business_router.get("/{business_id}/packages/prices/current", status_code=200,response_model=List[PackagePriceRead] , tags=["business - package - price"])
def get_current_price_of_business(
        business_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get the current price of business, owner and admin only"""
    return service.get_price_for_business(business_id=business_id, current_user=current_user, is_current=True, is_personal=None)

##Category
@business_router.post("/categories", status_code=201, response_model=PackageCategoryRead, tags=["business - package - category"])
def create_package_category(
        package_category: PackageCategoryCreate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Create a new package category for business owner and admin"""
    return service.create_category(data=package_category, current_user=current_user)

@business_router.get("/{business_id}/categories",response_model=List[PackageCategoryRead], status_code=200, tags=["business - package - category"])
def get_package_categories_for_business(
        business_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get the list of all package categories for business"""
    return service.get_category(business_id=business_id, category_id=None, current_user=current_user)

@business_router.patch("/categories", status_code=200, response_model=PackageCategoryRead, tags=["business - package - category"])
def update_package_category(
        data : PackageCategoryUpdate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Update a package category for business owner and admin"""
    return service.update_category(data=data, current_user=current_user)

@business_router.delete("/categories/{category_id}", status_code=204, tags=["business - package - category"])
def delete_package_category(
        category_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Delete a package category for business, owner and admin only"""
    return service.delete_category(category_id=category_id, current_user=current_user)

## BusinessMemberForm
@business_router.post("/members/forms", status_code=201, response_model=BusinessMemberFormRead, tags=["business - member - form"])
def create_business_member_form(
        member: BusinessMemberFormCreate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY):
    """Create a new business member form for business, owner and admin only"""
    return service.create_member_form(data=member, current_user= current_user)

@business_router.get("/{business_id}/members/{member_id}/forms", status_code=200, response_model=List[BusinessMemberFormRead], tags=["business - member - form"])
def get_business_member_forms(business_id:int,
                              member_id:int,
                              service: PACKAGE_SERVICE_DEP,
                              current_user: CURRENT_USER_DEPENDENCY):
    """Get the business member forms for business, owner and admin only"""
    return service.get_member_form(business_id=business_id, member_id=member_id, current_user=current_user)

@business_router.get("/{business_id}/members/forms", status_code=200, response_model=List[BusinessMemberFormRead], tags=["business - member - form"])
def get_all_members_forms(
        business_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get the business member forms for business, owner and admin only"""
    return service.get_member_form_for_business(business_id=business_id, current_user=current_user)

@business_router.patch("/members/forms", status_code=200, response_model=BusinessMemberFormRead, tags=["business - member - form"])
def update_business_member_form(
                                form: BusinessMemberFormUpdate,
                                service: PACKAGE_SERVICE_DEP,
                                current_user: CURRENT_USER_DEPENDENCY):
    """Update a business member form for business, owner and admin only"""
    return service.update_member_form( data=form, current_user=current_user)

@business_router.delete("/members/forms/{form_id}", status_code=204, tags=["business - member - form"])
def delete_business_member_form(
                                form_id:int,
                                service: PACKAGE_SERVICE_DEP,
                                current_user: CURRENT_USER_DEPENDENCY):
    """Delete a business member form for business, owner and admin only"""
    return service.delete_member_form( form_id=form_id, current_user=current_user)

#member commission route



@business_router.post("/members/commissions", response_model=BusinessMemberCommissionsRead, status_code=201, tags=["business - member - commission"])
def create_member_commission(
        commissions:BusinessMemberCommissionsCreate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Create a new member commission for business, owner and admin only"""
    return service.create_member_commission(data=commissions, current_user=current_user)

@business_router.get("/members/{member_id}/{package_id}/commissions", response_model=BusinessMemberCommissionsRead, status_code=200, tags=["business - member - commission"])
def get_member_current_commission_on_package(
        member_id:int,
        package_id:int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get the current commission for package, owner and admin only"""
    return service.get_member_commission(
        member_id=member_id,
        package_id=package_id,
        current_user=current_user)

@business_router.get("/{business_id}/commissions", response_model=List[BusinessMemberCommissionsRead], tags=["business - member - commission"])
def get_business_commissions(
        business_id: int,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Get the list of all commissions for business, owner and admin only"""
    return service.get_business_commission(business_id=business_id, current_user=current_user)

@business_router.patch("/members/commissions", response_model=BusinessMemberCommissionsRead, status_code=200, tags=["business - member - commission"])
def update_member_commission(
        data: BusinessMemberCommissionsUpdate,
        service: PACKAGE_SERVICE_DEP,
        current_user: CURRENT_USER_DEPENDENCY
):
    """Update a member commission for business, owner and admin only"""
    return service.update_member_commission(data=data, current_user=current_user)


