import json
from typing import Any, Dict, Optional
from datetime import datetime
from app.models.appointment_model import AppointmentCreate
from app.repositories.appointments.appointment_repositories import AppointmentRepository
from app.repositories.business_member_repository import BusinessMemberRepository
from app.services import appointment_service
from app.db.models.business_member import BusinessMember


class JotformWebhookProcessing:
    """Service for processing Jotform webhooks"""

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
            client_name=JotformWebhookProcessing._extract_name(raw_request),
            client_email=raw_request.get("q4_email", ""),
            client_phone=raw_request.get("q5_phone"),
            appointment_date=JotformWebhookProcessing._parse_date(raw_request.get("q6_date"))
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
        name_field = JotformWebhookProcessing.get_key(raw_request, "name")
        if(isinstance(name_field, dict)):
            first_name = JotformWebhookProcessing.get_key(name_field, 'first')
            last_name = JotformWebhookProcessing.get_key(name_field, 'last')
            return f'{first_name} {last_name}'
        return str(name_field) if name_field else "Unknown"

    @staticmethod
    def _extract_email(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        email = JotformWebhookProcessing.get_key(raw_request, "email")
        return str(email) if email else "Unknown"

    @staticmethod
    def _extract_phone(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        phone_field = JotformWebhookProcessing.get_key(raw_request, "phone")
        if (isinstance(phone_field, dict)):
            area = JotformWebhookProcessing.get_key(phone_field, 'area')
            phone = JotformWebhookProcessing.get_key(phone_field, 'phone')
            return f'{area} {phone}'
        return str(phone_field) if phone_field else "Unknown"

    @staticmethod
    def _extract_date(raw_request: Dict[str, Any]) -> datetime:
        """Extract full name form jotform name field"""
        appointment_field = JotformWebhookProcessing.get_key(raw_request, "appointment")
        if (isinstance(appointment_field, dict)):
            date = JotformWebhookProcessing.get_key(appointment_field, 'date')
            return JotformWebhookProcessing._parse_date(date)
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

