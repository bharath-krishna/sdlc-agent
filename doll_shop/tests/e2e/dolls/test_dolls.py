import pytest

pytestmark = pytest.mark.dolls


def test_list_dolls_public(function_client):
    response = function_client.get("/api/dolls")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_doll_requires_auth(function_client):
    response = function_client.post("/api/dolls", json={
        "name": "Test Doll",
        "description": "A doll for testing",
        "price": 19.99, "type": "wooden", "weight": 1.0,
        "stock_quantity": 10,
    })
    assert response.status_code == 401


def test_create_doll(user_client):
    response = user_client.post("/api/dolls", json={
        "name": "Test Doll",
        "description": "A doll for testing",
        "price": 19.99, "type": "wooden", "weight": 1.0,
        "stock_quantity": 10,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Doll"
    assert "id" in data
