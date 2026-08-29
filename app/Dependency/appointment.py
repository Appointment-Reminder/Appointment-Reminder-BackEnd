from dishka import Provider, Scope, provide
from sqlmodel import Session

from app.adapters.sql_model_adapter.appointment.adapters.sql_model_appointment_repository_adapter import \
    SQLModelAppointmentRepositoryAdapter
from app.domain.appointment.guard.appointment_guard import AppointmentGuard
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.appointment.service.appointment_service import AppointmentService
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort


class AppointmentProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_appointment_repo(self, db: Session) -> AppointmentRepositoryPort:
        return SQLModelAppointmentRepositoryAdapter(db=db)

    @provide
    def get_appointment_guard(self,
                              repo: AppointmentRepositoryPort,
                              business_member_repo: BusinessMemberRepositoryPort) -> AppointmentGuard:
        return AppointmentGuard(
            appointment_repo=repo,
            business_member_repo=business_member_repo)

    @provide
    def get_appointment_service(self,
                                appointment_repo: AppointmentRepositoryPort,
                                business_member_repo: BusinessMemberRepositoryPort,
                                business_guard: BusinessGuard) -> AppointmentService:
        return AppointmentService(
            appointment_repo=appointment_repo,
            business_member_repo=business_member_repo,
            business_guard=business_guard
        )
