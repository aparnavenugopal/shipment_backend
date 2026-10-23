
from fastapi.testclient import TestClient

from training.main import app

client = TestClient(app)


def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "paths" in response.json()

def test_create_shipment_rejects_missing_fields():
    response = client.post(
        "/shipments/orm",
        json={},
    )

    assert response.status_code == 401 or response.status_code == 422
