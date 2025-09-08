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
