from datetime import datetime
from typing import List, Optional


#PYDANTIC MODEL
from app.models.package.package_model import PackageCreate, PackageUpdate, PackageRead
from app.models.package.package_price_model import PackagePriceCreate, PackagePriceUpdate
from app.repositories.business_member_repository import BusinessMemberRepository
from app.repositories.packages.package_price_repository import PackagePriceRepository
from app.repositories.packages.packages_repository import PackagesRepository
from app.models.package.package_category_model import PackageCategoryCreate, PackageCategoryUpdate
from app.models.Member.business_member_commissions import BusinessMemberCommissionsCreate, BusinessMemberCommissionsRead
from app.models.Member.busioness_member_form_model import BusinessMemberFormCreate, BusinessMemberFormUpdate

#SERVICE
from app.services.business.BusinessGuard import BusinessGuard
from app.services.package.package_guard import PackageGuard

#DB MODEL
from app.db.models.package.package import Package
from app.db.models.user import User
from app.db.models.package.package_category import PackageCategory
from app.db.models.package.package_price import PackagePrice
from app.db.models.Member.business_member_form import BusinessMemberForm
from app.db.models.Member.member_commision import MemberCommission


class PackageService:
    def __init__(
        self,
        package_repo: PackagesRepository,
        price_repo: PackagePriceRepository,
        member_repo: BusinessMemberRepository,
        business_guard: BusinessGuard,
        packages_guard: PackageGuard
    ):
        self.package_repo = package_repo
        self.price_repo = price_repo
        self.member_repo = member_repo
        self.business_guard = business_guard
        self.packages_guard = packages_guard

    def create(self,  data: PackageCreate, current_user: User) -> Package:
        self.business_guard.ensure_exists(business_id=data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)
        self.packages_guard.ensure_category_exist(package_category_id=data.category_id)

        package = Package(
            business_id=data.business_id,
            category_id=data.category_id,
            name=data.name,
            description = data.description,
            is_active = True,
            jotform_alias = "None"
        )
        return self.package_repo.create_package(package=package)


    def list(self, business_id: int, current_user: User) -> List[Package]:
        self.business_guard.ensure_exists(business_id=business_id)
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        self.business_guard.ensure_exists(business_id)

        return self.package_repo.get_packages_by_business_id(business_id)

    def get(self, package_id: int, current_user: User) -> Package:
        package = self.packages_guard.ensure_package_exist(package_id)
        self.business_guard.ensure_admin_or_owner(package.business_id, current_user.id)
        return package

    def get_by_alias(self, business_id: int, category_id: int, alias_raw_value:str) -> List[Package]:
        self.packages_guard.ensure_category_exist(category_id)

        return self.package_repo.find_package_by_alias(business_id, category_id, alias_raw_value)

    def update(self, data: PackageUpdate, current_user: User) -> Package:
        self.business_guard.ensure_exists(business_id=data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)
        self.packages_guard.ensure_category_exist(data.category_id)

        return self.package_repo.update_package(data)

    def delete(self, package_id: int, current_user: User) -> Package:
        package = self.packages_guard.ensure_package_exist(package_id)
        self.business_guard.ensure_admin_or_owner(business_id=package.business_id, user_id=current_user.id)

        self.package_repo.delete_package(package_id)
    ##CATEGORY
    def create_category(self, data: PackageCategoryCreate, current_user: User) -> PackageCategory:
        print(f"Create oacjage category {data.business_id} {data.name}")
        self.business_guard.ensure_exists(business_id=data.business_id)
        self.business_guard.ensure_admin_or_owner(data.business_id, current_user.id)

        category = PackageCategory(
            name=data.name,
            business_id=data.business_id,
        )
        return self.package_repo.create_package_category(category)

    def get_category(self, business_id: int, category_id: Optional[int], current_user: User) -> List[PackageCategory]:
        self.business_guard.ensure_admin_or_owner(business_id, current_user.id)

        if category_id is not None:
            return self.package_repo.get_category_by_id(category_id)
        return self.package_repo.get_categories_by_business(business_id)

    def update_category(self, data: PackageCategoryUpdate, current_user: User) -> PackageCategory:
        category = self.packages_guard.ensure_category_exist(package_category_id=data.id)
        self.business_guard.ensure_exists(business_id=category.business_id)
        self.business_guard.ensure_admin_or_owner(category.business_id, current_user.id)
        return self.package_repo.update_package_category(data)

    def delete_category(self, category_id: int, current_user: User) -> bool:
        category = self.packages_guard.ensure_category_exist(category_id)
        self.business_guard.ensure_admin_or_owner(category.business_id, current_user.id)

        return self.package_repo.delete_package_category(category_id)

    #PRICE
    def create_price(self, data: PackagePriceCreate, current_user: User) -> PackagePrice:
        package = self.packages_guard.ensure_package_exist(data.package_id)
        self.business_guard.ensure_admin_or_owner(package.business_id, current_user.id)

        packagePrice = PackagePrice(
            package_id=data.package_id,
            total_price=data.total_price,
            deposit_amount=data.deposit_amount,
            remaining_amount=data.remaining_amount,
            is_personal=data.is_personal,
            effective_from=data.effective_from,
        )
        return self.price_repo.create(package_price=packagePrice)

    def update_price(self, data: PackagePriceUpdate, current_user: User) -> PackagePrice:
        package = self.packages_guard.ensure_package_exist(data.package_id)
        self.business_guard.ensure_admin_or_owner(package.business_id, current_user.id)
        package_price = self.packages_guard.ensure_package_price_exist(data.id)
        return self.price_repo.update(data)

    def delete_price(self, price_id: int, current_user: User) -> bool:
        package_price = self.packages_guard.ensure_package_price_exist(price_id)
        package = self.packages_guard.ensure_package_exist(package_price.package_id)
        self.business_guard.ensure_exists(package.business_id)
        self.business_guard.ensure_admin_or_owner(package.business_id, current_user.id)

        self.price_repo.delete(price_id)
        return True

    def get_price(self, package_id:int, current_user: User, is_personal: Optional[bool], is_current: Optional[bool]) -> List[PackagePrice]:
        package = self.packages_guard.ensure_package_exist(package_id)
        business = self.business_guard.ensure_admin_or_owner(package.business_id, current_user.id)

        if is_current is not None and is_current:
            return self.price_repo.get_current_price(package_id, is_personal=is_personal)

        return self.price_repo.get_price_history(package_id=package_id)

    def get_price_for_business(self, business_id:int, current_user: User, is_personal: Optional[bool], is_current: Optional[bool]) -> List[PackagePrice]:
        business = self.business_guard.ensure_admin_or_owner(business_id, current_user.id)
        packages = self.list(business_id, current_user=current_user)

        prices = []
        for package in packages:
            price = self.get_price(package.id, current_user=current_user, is_personal=is_personal, is_current=is_current)
            if price is not None:
                prices.append(price)

        return prices

    def create_member_form(self, data: BusinessMemberFormCreate, current_user: User) -> BusinessMemberForm:
        #TODO Check that the category exist and the package is in a business where current user is admin or owner
        # TODO CHeck that the business member is in the business
        category = self.packages_guard.ensure_category_exist(data.category_id)
        self.business_guard.ensure_exists(business_id=category.business_id)
        business = self.business_guard.ensure_admin_or_owner(business_id=category.business_id, user_id=current_user.id)
        member = self.business_guard.ensure_member_exist(member_id=data.business_member_id)
        self.business_guard.ensure_is_a_member(business_id=category.business_id, user_id=member.user_id)

        #TODO Create webhook token for the business member form

        memberForm = BusinessMemberForm(
            business_member_id=data.business_member_id,
            category_id=data.category_id,
            jotform_field_map = data.jotform_field_map,
            is_active= True,
            created_at= datetime.now(),
            webhook_token= "CREATETOKEN"
        )
        return self.member_repo.create_form(memberForm)

    def get_member_form(self, business_id, member_id: int, current_user: User) -> BusinessMemberForm:
        member = self.business_guard.ensure_member_exist(member_id=member_id)
        self.business_guard.ensure_is_a_member(business_id=business_id, user_id=member.user_id)
        self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)

        return self.member_repo.get_forms_for_member(member_id)

    def get_member_form_for_business(self, business_id:int, current_user: User) -> BusinessMemberForm:
        self.business_guard.ensure_exists(business_id=business_id)
        self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)

        return self.member_repo.get_forms_by_business(business_id=business_id)

    def update_member_form(self, data: BusinessMemberFormUpdate, current_user: User) -> BusinessMemberForm:
        member = self.business_guard.ensure_member_exist(member_id=data.business_member_id)
        category = self.packages_guard.ensure_category_exist(data.category_id)
        self.business_guard.ensure_is_a_member(business_id=category.business_id, user_id=member.user_id)
        self.business_guard.ensure_admin_or_owner(business_id=category.business_id, user_id=current_user.id)
        return self.member_repo.update_form(data)

    def delete_member_form(self,form_id: int, current_user: User):
        form = self.business_guard.ensure_form_Exist(form_id=form_id)
        member = self.business_guard.ensure_member_exist(member_id=form.business_member_id)
        self.business_guard.ensure_admin_or_owner(business_id=member.business_id, user_id=current_user.id)
        self.member_repo.delete_form(form)

    def create_member_commission(self, data: BusinessMemberCommissionsCreate, current_user: User) -> BusinessMemberCommissionsCreate:
        package = self.packages_guard.ensure_package_exist(data.package_id)
        business = self.business_guard.ensure_exists(business_id=package.business_id)
        member = self.business_guard.ensure_member_exist(member_id=data.business_member_id)
        self.business_guard.ensure_admin_or_owner(business_id=package.business_id, user_id=current_user.id)
        self.business_guard.ensure_is_a_member(business_id=package.business_id, user_id= member.user_id)

        commission = MemberCommission(
            business_member_id=data.business_member_id,
            package_id=package.id,
            commission_percent = data.commission_percent,
            effective_from=data.effective_from,
        )
        return self.member_repo.set_commission(commission)

    def get_member_commission(self, member_id: int, package_id: Optional[int], current_user: User) -> MemberCommission:
        member = self.business_guard.ensure_member_exist(member_id=member_id)
        package = self.packages_guard.ensure_package_exist(package_id)
        self.business_guard.ensure_admin_or_owner(business_id=member.business_id, user_id=current_user.id)
        self.business_guard.ensure_is_a_member(business_id=package.business_id, user_id=member_id)

        if package_id is not None:
            return self.member_repo.get_current_commission(member_id=member_id, package_id=package_id)

        return self.member_repo.get_commission(member_id=member_id)

    def get_business_commission(self, business_id: int, current_user: User):
        self.business_guard.ensure_exists(business_id=business_id)
        self.business_guard.ensure_admin_or_owner(business_id=business_id, user_id=current_user.id)






