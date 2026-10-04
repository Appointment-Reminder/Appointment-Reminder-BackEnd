from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.addon.adapters.sql_model_addon_repository_adapter import \
    SQLModelAddonRepositoryAdapter
from app.adapters.sql_model_adapter.addon.adapters.sql_model_addon_price_repository_adapter import \
    SQLModelAddonPriceRepositoryAdapter
from app.domain.addon.guard.addon_guard import AddonGuard
from app.domain.addon.port.addon_price_repository_port import AddonPriceRepositoryPort
from app.domain.addon.port.addon_repository_port import AddonRepositoryPort
from app.domain.addon.service.addon_service import AddonService
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.package.guard.package_guard import PackageGuard


class AddonProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_addon_repo(self, db: Session) -> AddonRepositoryPort:
        return SQLModelAddonRepositoryAdapter(db=db)

    @provide
    def get_addon_price_repo(self, db: Session) -> AddonPriceRepositoryPort:
        return SQLModelAddonPriceRepositoryAdapter(db=db)

    @provide
    def get_addon_guard(self, addon_repo: AddonRepositoryPort) -> AddonGuard:
        return AddonGuard(addon_repo=addon_repo)

    @provide
    def get_addon_service(self,
                          addon_repo: AddonRepositoryPort,
                          price_repo: AddonPriceRepositoryPort,
                          addon_guard: AddonGuard,
                          business_guard: BusinessGuard,
                          package_guard: PackageGuard) -> AddonService:
        return AddonService(
            addon_repo=addon_repo,
            price_repo=price_repo,
            addon_guard=addon_guard,
            business_guard=business_guard,
            package_guard=package_guard,
        )
