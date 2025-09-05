def test_preview_reminder(client):
    payload = {
        "appointment_id": "1",
        "template": "Hello {Client}, your shoot is at {Location} on {Time}."
    }
    response = client.post("/reminders/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "preview"
    assert "Central Park" in data["message"]
    assert "Alice" in data["message"]


def test_send_reminder(client):
    payload = {
        "appointment_id": "2",
        "template": "Reminder for {Client}: {Location} at {Time}."
    }
    response = client.post("/reminders/send", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert "Studio A" in data["message"]
    assert "Bob" in data["message"]