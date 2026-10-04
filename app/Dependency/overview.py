from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.overview.adapters.sql_model_overview_read_adapter import \
    SQLModelOverviewReadAdapter
from app.domain.addon.port.appointment_addon_repository_port import AppointmentAddonRepositoryPort
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.overview.port.overview_read_port import OverviewReadPort
from app.domain.overview.service.business_overview_service import BusinessOverviewService


class OverviewProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_overview_read_repo(self, db: Session,
                               appointment_repo: AppointmentRepositoryPort,
                               appointment_addon_repo: AppointmentAddonRepositoryPort) -> OverviewReadPort:
        return SQLModelOverviewReadAdapter(
            db=db, appointment_repo=appointment_repo, appointment_addon_repo=appointment_addon_repo)

    @provide
    def get_business_overview_service(self,
                                      read_repo: OverviewReadPort,
                                      business_member_repo: BusinessMemberRepositoryPort,
                                      business_guard: BusinessGuard) -> BusinessOverviewService:
        return BusinessOverviewService(
            read_repo=read_repo, business_member_repo=business_member_repo, business_guard=business_guard)
