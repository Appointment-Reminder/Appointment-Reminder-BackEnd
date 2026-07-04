from typing import List, Optional

from app.models.Member.business_member_commissions import BusinessMemberCommissionsCreate, BusinessMemberCommissionsRead
from app.models.Member.busioness_member_form_model import BusinessMemberFormCreate, BusinessMemberFormRead, \
    BusinessMemberFormUpdate
from app.models.package.package_category_model import PackageCategoryCreate, PackageCategoryRead
from app.models.package.package_model import PackageCreate, PackageRead
from app.models.package.package_price_model import PackagePriceCreate, PackagePriceRead
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.business_repository import BusinessRepository

from app.db.models.user import User


def create_package(package_data: PackageCreate, current_user:User, business_member_repo: BusinessMemberRepository ) -> PackageRead:

    """Create a package for this business"""
    #TODO Check that the current user is the owner of this business
    #TODO Check that the category exist

def get_packages(business_id: Optional[int], package_id: Optional[int], current_user:User, business_member_repo: BusinessMemberRepository ) -> list[PackageRead]:
    """Get all packages can filter by business id or package id"""
    #TODO Check that the current user is a member of the business
    #TODO filter by either business id or package id


def update_package(package_id: int, current_user:User, business_member_repo: BusinessMemberRepository) -> PackageRead:
    """Update a package"""
    #TODO Check that the current user is an admin or owner of this business

def delete_package(package_id: int, current_user:User, business_member_repo: BusinessMemberRepository) -> bool:
    """Delete a package"""
    #TODO CHeck that the current user is an admin or an owner
    #TODO Return true if deleted properly return false else

def create_price(price_data: PackagePriceCreate, current_user:User) -> PackagePriceRead :
    """Create a package price"""
    #TODO Check that the user is owner or admin on the business
    #TODO Check that the package exist in the business
    #TODO Check that the prioce remaining etc match

def get_prices(package_id: int, is_current: bool, current_user:User ) -> List[PackagePriceRead]:
    """Get all package prices"""
    #TODO Check that the current user is part of the business
    #TODO Check that the package exist
    #TODO Return the list of package, only return the current one if is_current

def create_package_category(package_category_data: PackageCategoryCreate, current_user:User) -> PackageCategoryRead:
    """Create a package category"""
    #TODO Check that the current user is an owner or admin of the business in businessID
    #TODO Check that the current category is not already registered
    #TODO Create the category

def get_package_category(business_id: int, current_user:User ) -> List[PackageCategoryRead]:
    """Get all package categories"""
    #TODO Check that the business Exist
    #TODO Check that the current user is member of the business
    #TODO Get the list of package category for the business

def delete_package_category(package_category_id: int, current_user:User ) -> bool:
    """Delete a package category"""
    #TODO Check that the package category exist
    #TODO Check that no business reference the package category
    #TODO Later, allow another category to replace the deleting one in reference
    #TODO Check that the current user is admin or owner
    #TODO Delete category

def create_business_member_form(business_member_form_data: BusinessMemberFormCreate, current_user:User) -> BusinessMemberFormRead:
    """Create a business member form"""
    #TODO Check that the business member exist
    #TODO Check that the current user is admin or owner
    #TODO Check that the category exist for that business

def get_business_member_forms(business_member_id:int, current_user:User) -> List[BusinessMemberFormRead]:
    """Get all business member forms"""
    # TODO CHeck that the business member exist
    #TODO Check that the current user is admin or owner
    #TODO Return the list of all the forms attached to a specific member

def update_business_member_forms(business_member_for_data: BusinessMemberFormUpdate, current_user:User) -> BusinessMemberFormRead:
    """Update a business member form"""
    #TODO Check that the business member exist
    #TODO Check that the current user has rights on the business
    #TODO Check that the category exist
    #TODO Update the business form

def create_business_member_commission(business_member_commission_data: BusinessMemberCommissionsCreate, current_user:User) -> BusinessMemberCommissionsRead:
    """Create a business member commission"""
    #TODO Check that the business member exist
    #TODO CHeck that the current user has rights on the business
    #TODO Check that the package exist
    #TODO Create the commissions

def get_business_member_commissions(business_member_id:int, is_current: Optional[bool], package_id: Optional[int], current_user:User) -> List[BusinessMemberCommissionsRead]:
    """Get all business member commissions"""
    #TODO Check that the current user is admin or owner
    #TODO Check that the business member exist
    #TODO Filter by only the current one if is_current
    #TODO Filter by package id if set
    #TODO return the list of commissions for that business member

