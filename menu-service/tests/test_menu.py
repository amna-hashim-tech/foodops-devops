import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../app"))
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_full_menu():
    response = client.get("/menu")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert "name" in items[0]
    assert "price" in items[0]


def test_get_menu_by_category():
    response = client.get("/menu/mains")
    assert response.status_code == 200
    items = response.json()
    assert all(item["category"] == "mains" for item in items)


def test_get_menu_invalid_category():
    response = client.get("/menu/nonexistent")
    assert response.status_code == 404


def test_get_item_by_id():
    response = client.get("/item/1")
    assert response.status_code == 200
    assert response.json()["id"] == "1"
    assert response.json()["name"] == "Grilled Chicken Breast"


def test_get_item_not_found():
    response = client.get("/item/999")
    assert response.status_code == 404
