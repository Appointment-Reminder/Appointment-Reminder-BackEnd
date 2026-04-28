import json
from typing import Any, Dict, Optional
from datetime import datetime
from app.db.models import appointment
from app.db.models.user import User
from app.db.session import Session
from app.models.appointment_model import AppointmentCreate
from app.repositories.appointment_repositories import AppointmentRepository
from app.services import appointment_service


class JotformService:
    """Service for processing Jotform webhooks"""

    @staticmethod
    def process_webhook(repository: AppointmentRepository, payload: Dict[str, Any], photographer_id: int):
        """
        Process Jotform webhook payload and create appointment

        :param repository:
        :param payload: Raw webhook payload from jotform
        :param photographer_id: ID of photographer receiving the submission
        :return: Create appointment object
        """


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


        appointment_data = AppointmentCreate(
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            appointment_date=appointment_date,
        )

        created_appointment = appointment_service.create_appointment(repository= repository, appointment_data = appointment_data, photographer_id = photographer_id)

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
    def validate_photographer(repository : AppointmentRepository, photographer_id: int) -> bool:
        """Verify photographer exists (if you have Photographer model)"""
        # TODO: Implement when Photographer model exists
        photographer = db.get(User, photographer_id)
        repository.get
        if photographer is not  None:
            return True

        print(f"Photographer not valid id : {photographer_id}")
        return False

