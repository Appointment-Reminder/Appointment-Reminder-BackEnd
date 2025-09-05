def test_list_appointments(client):
    response = client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]


def test_get_single_appointment(client):
    response = client.get("/appointments/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert "Alice" in data["name"]


def test_get_nonexistent_appointment(client):
    response = client.get("/appointments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"