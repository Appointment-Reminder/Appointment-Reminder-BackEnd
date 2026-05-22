from unittest.mock import Mock

import pytest

from app.models.appointment_model import AppointmentCreate
from app.repositories.appointment_repositories import AppointmentRepository
from app.services import appointment_service
from app.db.models.appointment import Appointment


@pytest.fixture
def appointment_repo():
    return Mock()

@pytest.fixture
def appointment_create():
    return AppointmentCreate(client_name="test", client_email="test@test.com", client_phone="123", appointment_date="2021-04-01", business_id=1, user_id=None)

@pytest.fixture
def fake_appointment():
    return Appointment(
        client_name="test",
        client_email="test@test.com",
        client_phone="123",
        appointment_date="2021-04-01",
        business_id=None,
        user_id=None
    )
def test_create_appointment_without_photographer_id_return_appointment(appointment_repo, appointment_create):
    appointment_repo.create.side_effect = lambda appointment: appointment

    result = appointment_service.create_appointment(repository= appointment_repo, appointment_data=appointment_create)

    assert isinstance(result, Appointment)
    assert result.user_id is None

def test_create_appointment_without_business_id_return_none(appointment_repo, appointment_create):
    appointment_repo.create.side_effect = lambda appointment: appointment

    appointment_without_business = appointment_create
    appointment_without_business.business_id = None
    result = appointment_service.create_appointment(appointment_repo, appointment_create)

    assert result is None

def test_create_appointment_calls_repo(appointment_repo, appointment_create):
    appointment_repo.create.side_effect = lambda appointment: appointment

    appointment_service.create_appointment(
        repository=appointment_repo,
        appointment_data=appointment_create,
    )

    appointment_repo.create.assert_called_once()

def test_create_appointment_base_status_is_pending(appointment_repo, appointment_create):
    appointment_repo.create.side_effect = lambda appointment: appointment

    result = appointment_service.create_appointment(
        repository=appointment_repo,
        appointment_data=appointment_create,
    )

    assert result.status == 'pending'


def test_get_appointment_by_photographer_call_get_appointment_by_photographer(appointment_repo):
    result = appointment_service.get_appointments_by_photographer(appointment_repo, photographer_id=1)
    appointment_repo.get_appointments_by_photographer.assert_called_once()

def test_get_appointment_by_id_call_get_appointment_by_id(appointment_repo):
    result = appointment_service.get_appointment_by_id(appointment_repo, appointment_id=1)
    appointment_repo.get_appointments_by_id.assert_called_once()

def test_update_appointment_call_update_appointment(appointment_repo, appointment_create):
    result = appointment_service.update_appointment(appointment_repo, appointment_id=1, appointment_data=appointment_create)
    appointment_repo.update.assert_called_once()

def test_appointment_delete_call_repo_delete_appointment(appointment_repo):
    result = appointment_service.delete_appointment(appointment_repo, appointment_id=1)
    appointment_repo.delete.assert_called_once()
