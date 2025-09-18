
def test_preview_reminder(reminders_client):
    payload = {
        "appointment_id": "1",
        "template": "Hello {Client}, your appointment is at {Time} in {Location}."
    }
    response = reminders_client.post("/reminders/preview", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "preview"
    assert "Alice" in data["message"]  # From DUMMY_APPOINTMENTS[0]
    assert "Central Park" in data["message"]


def test_send_reminder(reminders_client, capsys):
    payload = {
        "appointment_id": "2",
        "template": "Reminder for {Client}: meet at {Location} at {Time}."
    }
    response = reminders_client.post("/reminders/send", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert "Bob" in data["message"]

    # Check print output (optional)
    captured = capsys.readouterr()
    assert "Sending message to Bob Johnson" in captured.out


def test_reminder_invalid_appointment(reminders_client):
    payload = {
        "appointment_id": "999",
        "template": "Hello {Client}"
    }
    response = reminders_client.post("/reminders/preview", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"
def test_list_reminders(reminders_client):
    response = reminders_client.get("/reminders/")
    assert response.status_code == 200
    data =response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "r1"

def test_get_single_reminder(reminders_client):
    response = reminders_client.get("/reminders/r1")
    assert response.status_code == 200
    assert response.json()["id"] == "r1"

def test_create_reminder(reminders_client):
    payload = {"id": "r2", "appointment_id": "1", "template": "Hi {Client}", "status": "pending"}
    response = reminders_client.post("/reminders/", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == "r2"

def test_update_reminder(reminders_client):
    payload = {"id": "r1", "appointment_id": "1", "template": "Updated {Client}", "status": "sent"}
    response = reminders_client.put("/reminders/r1", json=payload)
    assert response.status_code == 200
    assert response.json()["template"] == "Updated {Client}"

def test_delete_reminder(reminders_client):
    response = reminders_client.delete("/reminders/r1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

