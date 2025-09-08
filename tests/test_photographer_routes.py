def test_list_photographers(photographers_client):
    response = photographers_client.get("/photographers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] in ["Eve", "Mallory"]

def test_list_photographers(photographers_client):
    response = photographers_client.get("/photographers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] in ["Eve", "Mallory"]

def test_get_nonexistent_photographer(photographers_client):
    response = photographers_client.get("/photographers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Photographer not found"
