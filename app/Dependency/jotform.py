from dishka import Scope, provide, Provider
from sqlmodel import Session

from app.adapters.sql_model_adapter.jotform.adapters.sql_model_jotform_repository_adapter import \
    SQLModelJotformRepositoryAdapter
from app.domain.Jotform.guard.jotform_guard import JotformGuard
from app.domain.Jotform.port.jotform_repository_port import JotformRepositoryPort
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
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
    def get_jotform_service(self,
                            business_guard: BusinessGuard,
                            jotform_guard: JotformGuard,
                            package_repo: PackageRepositoryPort,
                            member_repo: BusinessMemberRepositoryPort,
                            jotform_repo: JotformRepositoryPort) -> JotformService:
        return JotformService(
            business_guard=business_guard,
            jotform_guard=jotform_guard,
            package_repo=package_repo,
            member_repo=member_repo,
            jotform_repo=jotform_repo
        )
