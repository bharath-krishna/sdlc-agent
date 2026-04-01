import pytest

pytestmark = pytest.mark.orders


def test_create_order(user_client):
    # Create a doll first
    doll_response = user_client.post("/api/dolls", json={
        "name": "Order Doll",
        "description": "A doll for ordering",
        "price": 50.0, "type": "wooden", "weight": 1.0,
        "stock_quantity": 5,
    })
    doll_id = doll_response.json()["id"]

    # Create a customer first
    customer_response = user_client.post("/api/customers", json={
        "name": "Order Customer",
        "email": "order_unique_1774924687@example.com", "phone": "1234567890",
    })
    customer_id = customer_response.json()["id"]

    # Create an order
    order_response = user_client.post("/api/orders", json={
        "customer_id": customer_id,
        "items": [
            {"doll_id": doll_id, "quantity": 2}
        ]
    })
    assert order_response.status_code == 200
    order_data = order_response.json()
    assert order_data["customer_id"] == customer_id
    assert order_data["total_amount"] == 100.0
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["doll_id"] == doll_id
    assert order_data["items"][0]["quantity"] == 2


def test_create_order_insufficient_stock(user_client):
    # Create a doll first
    doll_response = user_client.post("/api/dolls", json={
        "name": "Low Stock Doll",
        "description": "A doll for ordering",
        "price": 50.0, "type": "wooden", "weight": 1.0,
        "stock_quantity": 1,
    })
    doll_id = doll_response.json()["id"]

    # Create a customer first
    customer_response = user_client.post("/api/customers", json={
        "name": "Order Customer 2",
        "email": "order2_unique_1774924687@example.com", "phone": "1234567890",
    })
    customer_id = customer_response.json()["id"]

    # Create an order with quantity 2
    order_response = user_client.post("/api/orders", json={
        "customer_id": customer_id,
        "items": [
            {"doll_id": doll_id, "quantity": 2}
        ]
    })
    assert order_response.status_code == 400
    assert "Insufficient stock" in order_response.json()["detail"]["message"]
