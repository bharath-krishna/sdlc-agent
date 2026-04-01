import pytest
from datetime import datetime, timedelta

pytestmark = pytest.mark.reservations


def test_create_reservation(user_client):
    # Create a doll first
    doll_response = user_client.post("/api/dolls", json={
        "name": "Reservation Doll",
        "description": "A doll for reservation",
        "price": 50.0,
        "type": "wooden",
        "weight": 0.5,
        "stock_quantity": 5,
    })
    assert doll_response.status_code == 200
    doll_id = doll_response.json()["id"]

    # Create a reservation
    start_time = (datetime.utcnow() + timedelta(hours=1)).replace(microsecond=0).isoformat()
    res_response = user_client.post("/api/reservations", json={
        "doll_id": doll_id,
        "start_time": start_time,
    })
    assert res_response.status_code == 200
    res_data = res_response.json()
    assert res_data["doll_id"] == doll_id
    # Check if start_time in response matches (ignoring Z or +00:00 suffix if present)
    assert res_data["start_time"].startswith(start_time)

def test_list_reservations(user_client):
    # List reservations
    response = user_client.get("/api/reservations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_cancel_reservation(user_client):
    # Create a doll
    doll_response = user_client.post("/api/dolls", json={
        "name": "Cancel Doll",
        "description": "A doll for cancellation",
        "price": 50.0,
        "type": "plastic",
        "weight": 0.2,
        "stock_quantity": 5,
    })
    assert doll_response.status_code == 200
    doll_id = doll_response.json()["id"]

    # Create a reservation
    start_time = (datetime.utcnow() + timedelta(hours=2)).replace(microsecond=0).isoformat()
    res_response = user_client.post("/api/reservations", json={
        "doll_id": doll_id,
        "start_time": start_time,
    })
    res_id = res_response.json()["id"]

    # Cancel reservation
    del_response = user_client.delete(f"/api/reservations/{res_id}")
    assert del_response.status_code == 200

    # Verify it's gone
    list_response = user_client.get("/api/reservations")
    ids = [r["id"] for r in list_response.json()]
    assert res_id not in ids

def test_overlapping_reservation(user_client):
     # Create a doll
    doll_response = user_client.post("/api/dolls", json={
        "name": "Overlap Doll",
        "description": "A doll for overlap check",
        "price": 50.0,
        "type": "cloth",
        "weight": 0.3,
        "stock_quantity": 5,
    })
    assert doll_response.status_code == 200
    doll_id = doll_response.json()["id"]

    # Create first reservation
    start_time1 = (datetime.utcnow() + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    user_client.post("/api/reservations", json={
        "doll_id": doll_id,
        "start_time": start_time1.isoformat(),
    })

    # Try creating second reservation that overlaps (starts 30 mins after first)
    start_time2 = (start_time1 + timedelta(minutes=30)).isoformat()
    res_response = user_client.post("/api/reservations", json={
        "doll_id": doll_id,
        "start_time": start_time2,
    })
    assert res_response.status_code == 400
    assert res_response.json()["detail"]["reason"] == "Reservation overlap"

def test_invalid_reservation_time(user_client):
     # Create a doll
    doll_response = user_client.post("/api/dolls", json={
        "name": "Past Doll",
        "description": "A doll for past time check",
        "price": 50.0,
        "type": "ceramic",
        "weight": 1.0,
        "stock_quantity": 5,
    })
    assert doll_response.status_code == 200
    doll_id = doll_response.json()["id"]

    # Try creating reservation in the past
    start_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    res_response = user_client.post("/api/reservations", json={
        "doll_id": doll_id,
        "start_time": start_time,
    })
    assert res_response.status_code == 400
    assert res_response.json()["detail"]["reason"] == "Invalid reservation time"
