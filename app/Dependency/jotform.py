from dishka import Scope, provide, Provider
from sqlmodel import Session

from app.adapters.jotform.APIJotformPort import JotformClientAdapter
from app.adapters.sql_model_adapter.jotform.adapters.sql_model_jotform_repository_adapter import \
    SQLModelJotformRepositoryAdapter
from app.domain.Jotform.guard.jotform_guard import JotformGuard
from app.domain.Jotform.port import jotform_port
from app.domain.Jotform.port.jotform_port import JotformPort
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.Jotform.service.jotform_webhook_service import JotformWebhookService
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort
from app.domain.package.port.package_repository_port import PackageRepositoryPort


class JotformProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_jotform_repo(self, db: Session) -> JotformRepositoryPort:
        return SQLModelJotformRepositoryAdapter(db=db)

    @provide
    def get_jotform_guard(self, repo: JotformRepositoryPort) -> JotformGuard:
        return JotformGuard(jotform_repo=repo)

    @provide
    def get_jotform_api(self) -> JotformPort:
        return JotformClientAdapter();
    @provide
    def get_jotform_service(self,
                            business_guard: BusinessGuard,
                            jotform_guard: JotformGuard,
                            package_repo: PackageRepositoryPort,
                            member_repo: BusinessMemberRepositoryPort,
                            jotform_repo: JotformRepositoryPort,
                            jotform_api: JotformPort,
                            ) -> JotformService:
        return JotformService(
            business_guard=business_guard,
            jotform_guard=jotform_guard,
            package_repo=package_repo,
            member_repo=member_repo,
            jotform_repo=jotform_repo,
            jotform_api=jotform_api
        )

    @provide
    def get_jotform_webhook_service(
            self,
            jotform_guard: JotformGuard,
            jotform_service: JotformService,
            package_guard: PackageGuard,
            business_guard: BusinessGuard,
            member_repo: BusinessMemberRepositoryPort,
            price_repo: PackagePriceRepositoryPort,
            appointment_repo: AppointmentRepositoryPort,
    ) -> JotformWebhookService:
        return JotformWebhookService(
            jotform_guard=jotform_guard,
            jotform_service=jotform_service,
            package_guard=package_guard,
            business_guard=business_guard,
            member_repo=member_repo,
            price_repo=price_repo,
            appointment_repo=appointment_repo,
        )