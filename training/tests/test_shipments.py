from types import SimpleNamespace
from unittest.mock import MagicMock
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from training.database_orm import get_db
from training.main import app
from training.router import shipments as shipment_routes


@pytest.fixture
def client():
    db = MagicMock()
    app.state.test_db = db
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_shipment(**overrides):
    values = {
        "id": 7,
        "content": "Laptop",
        "destination": "Hyderabad",
        "status": "pending",
        "customer_id": 1,
        "customer": SimpleNamespace(id=1, name="Krishna"),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_list_shipments_orm_returns_shipments_and_customers(client):
    shipment = make_shipment()
    db = app.state.test_db
    db.query.return_value.all.return_value = [shipment]

    response = client.get("/shipments/orm")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 7,
            "content": "Laptop",
            "destination": "Hyderabad",
            "status": "pending",
            "customer_id": 1,
            "customer": {"id": 1, "name": "Krishna"},
        }
    ]


def test_create_shipment_orm_passes_customer_id(client, monkeypatch):
    create = MagicMock(return_value=make_shipment())
    monkeypatch.setattr(shipment_routes, "create_shipment_orm_record", create)

    response = client.post(
        "/shipments/orm",
        json={
            "content": "Laptop",
            "destination": "Hyderabad",
            "status": "pending",
            "customer_id": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["customer"] == {"id": 1, "name": "Krishna"}
    assert create.call_args.args[1].customer_id == 1


def test_create_shipment_orm_rejects_invalid_payload(client, monkeypatch):
    create = MagicMock()
    monkeypatch.setattr(shipment_routes, "create_shipment_orm_record", create)

    response = client.post(
        "/shipments/orm",
        json={"content": "", "destination": "Hyderabad"},
    )

    assert response.status_code == 422
    create.assert_not_called()


def test_get_shipment_orm_by_id_returns_404_when_missing(client, monkeypatch):
    monkeypatch.setattr(
        shipment_routes, "get_shipment_by_id_orm", lambda db, shipment_id: None
    )

    response = client.get("/shipments/orm/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "shipment not found"


def test_patch_shipment_orm_sends_only_provided_fields(client, monkeypatch):
    update = MagicMock(return_value=make_shipment(destination="Chennai"))
    monkeypatch.setattr(shipment_routes, "update_shipment_part_orm", update)

    response = client.patch(
        "/shipments/orm/7",
        json={"destination": "Chennai"},
    )

    assert response.status_code == 200
    assert update.call_args.args[1:] == (7, {"destination": "Chennai"})


def test_put_shipment_orm_replaces_fields(client, monkeypatch):
    replace = MagicMock(return_value=make_shipment(customer_id=None, customer=None))
    monkeypatch.setattr(shipment_routes, "replace_shipment_full_orm", replace)

    response = client.put(
        "/shipments/orm/7",
        json={
            "content": "Phone",
            "destination": "Delhi",
            "status": "in_transit",
        },
    )

    assert response.status_code == 200
    assert replace.call_args.args[1:] == (
        7,
        {
            "content": "Phone",
            "destination": "Delhi",
            "status": "in_transit",
            "customer_id": None,
        },
    )


def test_delete_shipment_orm_returns_no_content(client, monkeypatch):
    delete = MagicMock(return_value=True)
    monkeypatch.setattr(shipment_routes, "delete_shipment_orm_record", delete)

    response = client.delete("/shipments/orm/7")

    assert response.status_code == 204
    assert response.content == b""
    assert delete.call_args.args[1] == 7


def test_delete_shipment_orm_returns_404_when_missing(client, monkeypatch):
    monkeypatch.setattr(shipment_routes, "delete_shipment_orm_record", lambda db, shipment_id: False)

    response = client.delete("/shipments/orm/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "shipment not found"
