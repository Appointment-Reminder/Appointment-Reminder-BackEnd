from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.business.adapters.sql_model_business_member_repository_adapter import \
    SQLModelBusinessMemberRepositoryAdapter
from app.adapters.sql_model_adapter.business.adapters.sql_model_business_repository_adapter import \
    SQLModelBusinessRepositoryAdapter

from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.business.port.business_repository_port import BusinessRepositoryPort
from app.domain.business.service.business_service import BusinessService
from app.domain.user.guard.user_guard import UserGuard


class BusinessProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_business_repo(self, db: Session) -> BusinessRepositoryPort:
        return SQLModelBusinessRepositoryAdapter(db)

    @provide
    def get_business_member_repo(self, db: Session) -> BusinessMemberRepositoryPort:
        return SQLModelBusinessMemberRepositoryAdapter(db)

    @provide
    def get_business_guard(self, repo: BusinessRepositoryPort, business_member_repo: BusinessMemberRepositoryPort) -> BusinessGuard:
        return BusinessGuard(business_repo=repo, business_member_repo=business_member_repo)

    @provide
    def get_business_service(self, repo: BusinessRepositoryPort, member_repo: BusinessMemberRepositoryPort, guard: BusinessGuard, user_guard: UserGuard) -> BusinessService:
        return BusinessService(business_repo= repo, guard=guard, member_repo=member_repo, user_guard=user_guard)