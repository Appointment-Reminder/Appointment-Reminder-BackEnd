from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.package.adapters.sql_model_package_price_repository_adapter import \
    SQLModelPackagePriceRepositoryAdapter
from app.adapters.sql_model_adapter.package.adapters.sql_model_package_repository_adapter import \
    SQLModelPackageRepositoryAdapter
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort
from app.domain.package.port.package_repository_port import PackageRepositoryPort
from app.domain.package.service.package_service import PackageService


class PackageProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_package_repo(self, db: Session) -> PackageRepositoryPort:
        return SQLModelPackageRepositoryAdapter(db=db)

    @provide
    def get_package_price_repo(self, db: Session) -> PackagePriceRepositoryPort:
        return SQLModelPackagePriceRepositoryAdapter(db=db)

    @provide
    def get_package_guard(self, package_repo: PackageRepositoryPort, package_price_repo: PackagePriceRepositoryPort) -> PackageGuard:
        return PackageGuard(package_repo=package_repo, package_price_repo=package_price_repo)

    @provide
    def get_package_service(self,
                            package_repo: PackageRepositoryPort,
                            package_price_repo: PackagePriceRepositoryPort,
                            package_guard: PackageGuard,
                            member_repo: BusinessMemberRepositoryPort,
                            business_guard: BusinessGuard) -> PackageService:
        return PackageService(
            package_repo= package_repo,
            price_repo= package_price_repo,
            member_repo= member_repo,
            business_guard= business_guard,
            packages_guard= package_guard
        )