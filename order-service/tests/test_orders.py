import pytest
import respx
import httpx
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../app"))

# Set menu service URL before importing app
os.environ["MENU_SERVICE_URL"] = "http://menu-service:8000"
from main import app

client = TestClient(app)

MOCK_MENU_ITEM = {
    "id": "1",
    "name": "Chicken Shawarma",
    "category": "mains",
    "price": 25.0,
    "available": True
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@respx.mock
def test_place_order_success():
    respx.get("http://menu-service:8000/item/1").mock(
        return_value=httpx.Response(200, json=MOCK_MENU_ITEM)
    )
    response = client.post("/order", json={
        "customer_name": "Amna",
        "items": [{"item_id": "1", "quantity": 2}]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Amna"
    assert data["total_price"] == 50.0
    assert data["status"] == "confirmed"
    assert "order_id" in data


@respx.mock
def test_place_order_invalid_item():
    respx.get("http://menu-service:8000/item/999").mock(
        return_value=httpx.Response(404, json={"detail": "Not found"})
    )
    response = client.post("/order", json={
        "customer_name": "Amna",
        "items": [{"item_id": "999", "quantity": 1}]
    })
    assert response.status_code == 400


def test_get_order_not_found():
    response = client.get("/order/FAKEID")
    assert response.status_code == 404
