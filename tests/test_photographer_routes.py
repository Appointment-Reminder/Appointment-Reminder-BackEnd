from app.models.photographer import Photographer


def test_list_photographers(photographers_client):
    response = photographers_client.get("/photographers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] in ["Eve", "Mallory"]

def test_get_single_photographer(photographers_client):
    response = photographers_client.get("/photographers/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Eve"

def test_create_photographer(photographers_client):
    payload = {"id": "3", "name": "john", "email": "john@example.com"}
    response = photographers_client.post("/photographers/", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == "3"
    assert response.json()["name"] == "john"

def test_update_photographer(photographers_client):
    payload = {"id": "2", "name": "Jacques", "email": "example@email.com"}
    response = photographers_client.put("/photographers/2", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Jacques"

def test_delete_photographer(photographers_client):
    response = photographers_client.delete("/photographers/1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

def test_get_nonexistent_photographer(photographers_client):
    response = photographers_client.get("/photographers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Photographer not found"
