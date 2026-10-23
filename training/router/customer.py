from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from ..database_orm import get_db
from ..model import CustomerCreate, CustomerModify
from ..services.customer_service import (
    insert_customer,
    CustomerAlreadyLinkedError,
    CustomerUserNotFoundError,
    list_all_customers,
    fetch_customer_by_id,
    modify_customer_part,
    update_customer,
    delete_customer
)

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", status_code = status.HTTP_200_OK)
def get_all_customer(db: Session = Depends(get_db)):
    return list_all_customers(db)

@router.post("/", status_code = status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    try:
        return insert_customer(db, customer_data)
    except CustomerUserNotFoundError:
        raise HTTPException(status_code=404, detail="user not found")
    except CustomerAlreadyLinkedError:
        raise HTTPException(status_code=409, detail="user already has a customer profile")


@router.get("/{customer_id}", status_code = status.HTTP_201_CREATED)
def get_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = fetch_customer_by_id(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code = 404,
            detail = "customer not found"
        )

    return customer

@router.patch("/{customer_id}", status_code= status.HTTP_200_OK)
def update_customer_part_by_id(
    customer_id: int,
    customer_data: CustomerModify,
    db: Session = Depends(get_db)
):
    try:
        customer = modify_customer_part(db, customer_id, customer_data)
    except CustomerUserNotFoundError:
        raise HTTPException(status_code=404, detail="user not found")
    except CustomerAlreadyLinkedError:
        raise HTTPException(status_code=409, detail="user already has a customer profile")

    if customer is None:
        raise HTTPException(
        status_code=404,
            detail="customer not found"
        )

    return customer

@router.put("/{customer_id}", status_code = status.HTTP_200_OK)
def replace_customer(
    customer_id: int,
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    try:
        customer = update_customer(db, customer_id, customer_data)
    except CustomerUserNotFoundError:
        raise HTTPException(status_code=404, detail="user not found")
    except CustomerAlreadyLinkedError:
        raise HTTPException(status_code=409, detail="user already has a customer profile")

    if customer is None:
        raise HTTPException(
            status_code = 404,
            detail="customer not found"
        )

    return customer


@router.delete("/{customer_id}", status_code=204)
def remove_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_customer(db, customer_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return Response(status_code=204)
