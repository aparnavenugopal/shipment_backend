from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

from learn.schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate
from learn.db import Database


app = FastAPI()

db = Database()


# -----------------------------
# GET latest shipment
# -----------------------------
@app.get("/shipment/latest")
def get_latest_shipment():
    shipment = db.get_latest()

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shipments found"
        )

    return shipment


# -----------------------------
# GET shipment by ID
# -----------------------------
@app.get("/shipment/{id}", response_model=ShipmentRead)
def get_shipment(id: int):
    shipment = db.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment id doesn't exist"
        )

    return shipment


# -----------------------------
# CREATE shipment
# -----------------------------
@app.post("/shipment", status_code=status.HTTP_201_CREATED)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:

    result = db.create(shipment)

    return result


# -----------------------------
# UPDATE shipment - PATCH
# -----------------------------
@app.patch("/shipment/{id}", response_model=ShipmentRead)
def patch_shipment(
    id: int,
    shipment: ShipmentUpdate
):
    updated_shipment = db.update(id, shipment)

    if updated_shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment id doesn't exist"
        )

    return updated_shipment


# -----------------------------
# DELETE shipment
# -----------------------------
@app.delete("/shipment/{id}")
def delete_shipment(id: int) -> dict[str, str]:

    deleted = db.delete(id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment id doesn't exist"
        )

    return {
        "detail": f"Shipment with id #{id} deleted successfully"
    }


# -----------------------------
# Scalar documentation
# -----------------------------
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )