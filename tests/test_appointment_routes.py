
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





