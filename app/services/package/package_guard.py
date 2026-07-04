from fastapi import HTTPException

from app.repositories.packages.package_price_repository import PackagePriceRepository
from app.repositories.packages.packages_repository import PackagesRepository
from app.db.models.package.package import Package
from app.db.models.package.package_category import PackageCategory
from app.db.models.package.package_price import PackagePrice


class PackageGuard:
    def __init__(
            self,
            package_repo: PackagesRepository,
            package_price_repo: PackagePriceRepository,
    ):
        self.package_repo = package_repo
        self.package_price_repo = package_price_repo

    def ensure_category_exist(self, package_category_id: int) -> PackageCategory:
        category = self.package_repo.get_category_by_id(category_id = package_category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def ensure_package_exist(self, package_id: int) -> Package:
        package = self.package_repo.get_package_by_id(package_id = package_id)
        if package is None:
            raise HTTPException(status_code=404, detail="Package not found")
        return package

    def ensure_package_price_exist(self, package_price_id: int) -> PackagePrice:
        package_price = self.package_price_repo.get_package_price(package_price_id = package_price_id)
        if package_price is None:
            raise HTTPException(status_code=404, detail="Package price not found")
        return package_price