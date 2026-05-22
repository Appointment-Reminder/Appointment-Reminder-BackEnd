
import pytest
from google.api_core.datetime_helpers import utcnow
from pydantic import ValidationError

from app.models.appointment_model import AppointmentCreate


def test_empty_business_id():
    with pytest.raises(ValidationError):
        AppointmentCreate(client_name="test",
                          client_email="test@test.com",
                          client_phone="123",
                          user_id=1,
                          business_id=None,
                          appointment_date=utcnow())

def test_empty_user_id():
    appointment = AppointmentCreate(client_name="test",
                          client_email="test@test.com",
                          client_phone="123",
                          user_id=None,
                          business_id=1,
                          appointment_date=utcnow())
    assert appointment.client_name == "test"

def test_create_appointment_with_name_and_email():
    appointment = AppointmentCreate(client_name="test",
                                    client_email="test@test.com",
                                    client_phone="123",
                                    user_id=1,
                                    business_id=1,
                                    appointment_date=utcnow())
    assert appointment.client_name == "test"