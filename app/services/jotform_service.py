from typing import Any, Dict, Optional
from datetime import datetime
from app.db.models import appointment
from app.db.session import Session
from app.models.appointment_model import AppointmentCreate


class JotformService:
    """Service for processing Jotform webhooks"""

    @staticmethod
    def process_webhook(db: Session, payload: Dict[str, Any], photographer_id: int):
        """
        Process Jotform webhook payload and create appointment

        :param db: Database session
        :param payload: Raw webhook payload from jotform
        :param photographer_id: ID of photographer receiving the submission
        :return: Create appointment object
        """

        raw_request = payload.get('request', {})

        # Extract and transform jotform data
        appointment_data = JotformService._extract_appointment_data(raw_request)

        # Create appointment using appointment service
        appointment = appointment_service.create_appointment(db = db, appointment = appointment_data, photographer_id = photographer_id)

        #add jotform metadata
        appointment.jotform_submission_id = payload.get('submissionID')
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def find_field_by_name(
            data: Dict[str, Any],
            field_name: str,
    ) -> Optional[Any]:
        """ Find a field by searching for a name pattern in the keys"""
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
    def _extract_name(raw_request: Dict[str, Any]) -> str:
        """Extract full name form jotform name field"""
        name_field = raw_request.get('name', {})
        if(isinstance(name_field, dict)):
            first_name = name_field['firstName']
            last_name = name_field['lastName']
            return f'{first_name} {last_name}'
        return str(name_field) if name_field else "Unknown"

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
    def validate_photographer(db: Session, photographer_id: int) -> bool:
        """Verify photographer exists (if you have Photographer model)"""
        # TODO: Implement when Photographer model exists
        # photographer = db.get(Photographer, photographer_id)
        # return photographer is not None
        return True

