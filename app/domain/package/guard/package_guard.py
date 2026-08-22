from app.domain.package.errors.package_errors import PackageError
from app.domain.package.models.package import Package
from app.domain.package.models.package_category_model import PackageCategory
from app.domain.package.models.package_price import PackagePrice
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort
from app.domain.package.port.package_repository_port import PackageRepositoryPort


class PackageGuard:
    def __init__(
            self,
            package_repo: PackageRepositoryPort,
            package_price_repo: PackagePriceRepositoryPort,
    ):
        self.package_repo = package_repo
        self.package_price_repo = package_price_repo

    def ensure_category_exist(self, package_category_id: int) -> PackageCategory:
        category = self.package_repo.get_category_by_id(category_id = package_category_id)
        if category is None:
            raise PackageError()
        return category

    def ensure_package_exist(self, package_id: int) -> Package:
        package = self.package_repo.get_package_by_id(package_id = package_id)
        if package is None:
            raise PackageError()
        return package

    def ensure_package_price_exist(self, package_price_id: int) -> PackagePrice:
        package_price = self.package_price_repo.get_package_price(package_price_id = package_price_id)
        if package_price is None:
            raise PackageError()
        return package_price