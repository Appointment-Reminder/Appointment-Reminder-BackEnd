from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort


class AppointmentGuard:
    def __init__(self,
                 appointment_repo: AppointmentRepositoryPort,
                 business_member_repo: BusinessMemberRepositoryPort):
        self.appointment_repo = appointment_repo
        self.business_member_repo = business_member_repo

    ## TODO Check if appointment exist, if appointment is assigned to member etc