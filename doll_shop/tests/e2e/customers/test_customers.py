import pytest

pytestmark = pytest.mark.customers


def test_create_customer(user_client):
    response = user_client.post("/api/customers", json={
        "name": "Test Customer",
        "email": "test_unique_1774924687_final@example.com",
        "phone": "1234567890",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["email"] == "test_unique_1774924687_final@example.com"
    assert "id" in data


def test_create_customer_duplicate_email(user_client):
    user_client.post("/api/customers", json={
        "name": "Test Customer",
        "email": "duplicate_unique_1774924687_final@example.com",
        "phone": "1234567890",
    })
    response = user_client.post("/api/customers", json={
        "name": "Another Customer",
        "email": "duplicate_unique_1774924687_final@example.com",
        "phone": "0987654321",
    })
    assert response.status_code == 400
    assert response.json()["detail"]["reason"] == "Duplicated resource"
