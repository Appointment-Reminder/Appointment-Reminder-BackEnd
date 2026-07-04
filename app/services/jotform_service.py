import json
from typing import Any, Dict, Optional
from datetime import datetime
from app.models.appointment_model import AppointmentCreate
from app.repositories.appointments.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.services import appointment_service
from app.db.models.business_member import BusinessMember


class JotformService:
    """Service for processing Jotform webhooks"""

    @staticmethod
    def process_webhook(
            appointment_repository: AppointmentRepository,
            business_member_repository: BusinessMemberRepository,
            payload: Dict[str, Any],
            business_member_token: str):

        business_member = JotformService.validate_photographer(
                business_member_repo=business_member_repository,
                business_member_token= business_member_token)
        if not business_member:
            raise

        raw_request_str = payload.get('rawRequest', {})

        try:
            raw_request = json.loads(raw_request_str)

        except json.decoder.JSONDecodeError as e:
            raise ValueError(f"Failed to parse raw request: {e}")

        try:

            client_name = JotformService._extract_name(raw_request)
            client_email = JotformService._extract_email(raw_request)
            client_phone = JotformService._extract_phone(raw_request)
            appointment_date = JotformService._extract_date(raw_request)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

        print(business_member.business_id)

        appointment_data = AppointmentCreate(
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            appointment_date=appointment_date,
            business_id=business_member.business_id,
            user_id=business_member.user_id
        )

        created_appointment = appointment_service.create_appointment(repository= appointment_repository, appointment_data = appointment_data)

        if not created_appointment:
            raise ValueError("Appointment not created")

        return created_appointment

    @staticmethod
    def find_field_by_name(
            data: Dict[str, Any],
            field_name: str,
    ) -> Optional[Any]:
        find_name_lower = field_name.lower()

        for key in data.keys():
            if find_name_lower in key.lower():
                value = data.get(key)
                if value is None or value == '':
                    continue

                print(f"found '{field_name}' in '{key}'")
                return value
        print(f" No field found containing '{field_name}'")
        return None

    @staticmethod
    def _extract_appointment_data(raw_request: Dict[str, Any]) -> AppointmentCreate:
        """
        Extract appointment data from jotform raw request

        Note: Field Ids() need to match actual jotform

        :param raw_request:
        :return:
        """


        return AppointmentCreate(
            client_name=JotformService._extract_name(raw_request),
            client_email=raw_request.get("q4_email", ""),
            client_phone=raw_request.get("q5_phone"),
            appointment_date=JotformService._parse_date(raw_request.get("q6_date"))
        );

    @staticmethod
    def get_key(data: Dict[str, Any], search_key: str) -> Optional[Any]:
        search_key = search_key.lower()

        for key, value in data.items():
            if search_key in key.lower():
                return value

        return None

    @staticmethod
    def _extract_name(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        name_field = JotformService.get_key(raw_request, "name")
        if(isinstance(name_field, dict)):
            first_name = JotformService.get_key(name_field,'first')
            last_name = JotformService.get_key(name_field, 'last')
            return f'{first_name} {last_name}'
        return str(name_field) if name_field else "Unknown"

    @staticmethod
    def _extract_email(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        email = JotformService.get_key(raw_request, "email")
        return str(email) if email else "Unknown"

    @staticmethod
    def _extract_phone(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        phone_field = JotformService.get_key(raw_request, "phone")
        if (isinstance(phone_field, dict)):
            area = JotformService.get_key(phone_field, 'area')
            phone = JotformService.get_key(phone_field, 'phone')
            return f'{area} {phone}'
        return str(phone_field) if phone_field else "Unknown"

    @staticmethod
    def _extract_date(raw_request: Dict[str, Any]) -> datetime:
        """Extract full name form jotform name field"""
        appointment_field = JotformService.get_key(raw_request, "appointment")
        if (isinstance(appointment_field, dict)):
            date = JotformService.get_key(appointment_field, 'date')
            return JotformService._parse_date(date)
        return datetime.utcnow()

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse date from Jotform format"""
        if not date_str:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            # Try other common formats if needed
            return datetime.utcnow()

    @staticmethod
    def validate_photographer( business_member_repo: BusinessMemberRepository, business_member_token: str) -> Optional[BusinessMember]:
        """Verify photographer exists (if you have Photographer model)"""
        business_member = business_member_repo.get_member_by_token(token=business_member_token)

        if business_member is not  None:
            return business_member

        print(f"Photographer not valid token : {business_member_token}")
        return None

