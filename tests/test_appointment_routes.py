import pytest

def test_list_appointments(appointment_client):
    response = appointment_client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Alice"

def test_get_single_appointment(appointment_client):
    response = appointment_client.get("/appointments/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert data["name"] == "Alice"

def test_get_nonexistent_appointment(appointment_client):
    response = appointment_client.get("/appointments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"

def test_update_appointment(appointment_client):
    payload = {"id":"1", "name":"Jacques", "surname":"Smith", "phone":"+123456789",
                "email":"alice@example.com", "time":"2025-09-10 15:00", "location":"Central Park"}
    response = appointment_client.put("/appointments/1", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Jacques"

def test_update_nonexistent_appointment(appointment_client):
    payload = {"id": "1", "name": "Jacques", "surname": "Smith", "phone": "+123456789",
               "email": "alice@example.com", "time": "2025-09-10 15:00", "location": "Central Park"}
    response = appointment_client.put("/appointments/999", json=payload)
    assert response.status_code == 404

def test_delete_appointment(appointment_client):
    response = appointment_client.delete("/appointments/1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

def test_delete_nonexistent_appointment(appointment_client):
    response = appointment_client.delete("/appointments/4")
    assert response.status_code == 404

@pytest.mark.asyncio
def test_create_appointment(appointment_client):
    payload = {"id": "4", "name": "John", "surname": "Smith", "phone": "+123456789",
               "email": "alice@example.com", "time": "2025-09-10 15:00", "location": "Central Park"}
    response = appointment_client.post("/photographers/", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == "4"
    assert response.json()["name"] == "John"



