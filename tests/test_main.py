from fastapi.testclient import TestClient
from app.main import app  # adjust if your main.py is inside app/

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Photo Reminder"}
