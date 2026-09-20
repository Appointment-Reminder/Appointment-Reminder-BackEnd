# app/domain/Jotform/service/jotform_webhook_service.py
from datetime import datetime

from app.domain.Jotform.guard.jotform_guard import JotformGuard
from app.domain.Jotform.service.jotform_webhook_parser import parse_jotform_raw_request
from app.domain.Jotform.service.jotform_submission_assembler import resolve_booking_context
from app.domain.Jotform.service.jotform_service import JotformService
from app.domain.appointment.models.appointment_model import Appointment
from app.domain.appointment.port.appointment_repository_port import AppointmentRepositoryPort
from app.domain.business.guard.business_guard import BusinessGuard
from app.domain.business.port.business_member_repository_port import BusinessMemberRepositoryPort
from app.domain.package.guard.package_guard import PackageGuard
from app.domain.package.port.package_price_repository_port import PackagePriceRepositoryPort


class JotformWebhookService:
    def __init__(
        self,
        jotform_guard: JotformGuard,
        jotform_service: JotformService,
        package_guard: PackageGuard,
        business_guard: BusinessGuard,
        member_repo: BusinessMemberRepositoryPort,
        price_repo: PackagePriceRepositoryPort,
        appointment_repo: AppointmentRepositoryPort,
    ):
        self.jotform_guard = jotform_guard
        self.jotform_service = jotform_service
        self.package_guard = package_guard
        self.business_guard = business_guard
        self.member_repo = member_repo
        self.price_repo = price_repo
        self.appointment_repo = appointment_repo

    def process_submission(self, webhook_token: str, raw_request: dict) -> Appointment:
        form = self.jotform_guard.ensure_webhook_token_valid(webhook_token)
        credential = self.jotform_guard.ensure_credential_exists(form.credential_id)
        business_id = credential.business_id

        parsed_answers = parse_jotform_raw_request(raw_request)
        resolved = self.jotform_service.resolve_submission(form=form, raw_answers=parsed_answers)

        booking = resolve_booking_context(
            business_id=business_id,
            form_id=form.id,
            package_alias_raw=resolved.get("package") or "",
            package_guard=self.package_guard,
            jotform_guard=self.jotform_guard,
            member_repo=self.member_repo,
            price_repo=self.price_repo,
        )

        status = "pending" if booking.fully_resolved else "needs_assignment"

        appointment = Appointment(
            id=None,
            business_id=business_id,
            user_id=booking.member_id,
            package_id=booking.package_id,
            package_price_id=booking.package_price_id,
            form_id=form.id,
            client_name=resolved.get("client_name") or "",
            client_email="",  # not yet in SUBMISSION_FIELDS — see note below
            client_phone=None,
            price_at_booking=booking.price_at_booking,
            deposit_amount=booking.deposit_amount,
            remaining_amount=booking.remaining_amount,
            commission_percent_at_booking=booking.commission_percent_at_booking,
            commission_amount_at_booking=booking.commission_amount_at_booking,
            is_personal=booking.is_personal,
            appointment_date=resolved.get("appointment_date"),
            status=status,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user=None,
        )

        return self.appointment_repo.create(appointment)