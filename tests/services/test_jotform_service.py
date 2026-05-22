from unittest.mock import Mock, patch

import pytest
import json

from app.services.jotform_service import JotformService
from app.db.models.business_member import BusinessMember


@pytest.fixture
def mock_business_member():
    # Create a real BusinessMember object with actual values
    member = Mock(spec=BusinessMember)
    member.id = 1
    member.business_id = 10  # Real int, not Mock
    member.user_id = 5       # Real int, not Mock
    member.webhook_token = "test_token_123"
    member.role = "PHOTOGRAPHER"
    return member

@pytest.fixture
def mock_appointment_repo():
    return Mock()

@pytest.fixture
def mock_business_member_repo():
    return Mock()

@pytest.fixture
def valid_jotform_payload():
    raw_data = {
        "q3_name": {"first": "test", "last": "test"},
        "q4_email": "test@test.com",
        "q5_phone": "1234567890",
        "q6_appointmentDate": "2024-05-15"
    }
    return {
        "rawRequest": json.dumps(raw_data)
    }


def test_process_webhook_success(mock_appointment_repo, mock_business_member_repo,valid_jotform_payload, mock_business_member):


    # Mock successful appointment creation
    mock_appointment = Mock(spec=BusinessMember)
    mock_appointment.id = 1
    mock_appointment_repo.create.return_value = mock_appointment

    with patch.object(JotformService, 'validate_photographer', return_value=mock_business_member):
        result = JotformService.process_webhook(
            appointment_repository=mock_appointment_repo,
            business_member_repository=mock_business_member_repo,
            payload=valid_jotform_payload,
            business_member_token="test_token_123"
        )

    assert result is not None
    assert result.id == 1


def test_process_webhook_invalid_token(mock_appointment_repo, mock_business_member_repo, valid_jotform_payload):
    mock_business_member_repo.get_by_webhook_token.return_value = None

    with pytest.raises(Exception):  # Replace with your specific exception
        JotformService.process_webhook(
            appointment_repository=mock_appointment_repo,
            business_member_repository=mock_business_member_repo,
            payload=valid_jotform_payload,
            business_member_token="invalid_token"
        )


def test_process_webhook_invalid_json(mock_appointment_repo, mock_business_member_repo, mock_business_member):

    invalid_payload = {"rawRequest": "not valid json{"}

    with pytest.raises(ValueError, match="Failed to parse raw request"):
        JotformService.process_webhook(
            appointment_repository=mock_appointment_repo,
            business_member_repository=mock_business_member_repo,
            payload=invalid_payload,
            business_member_token="test_token_123"
        )