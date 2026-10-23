from fastapi import APIRouter,HTTPException, Body, status, Response
from sqlalchemy.orm import Session
from fastapi import Depends
from ..celery.tasks import send_shipment_email

from ..model import ShipmentCreate, ShipmentModify, ShipmentResponse
from ..services.shipment_service import (
    get_all_shipments,
    insert_shipment,
    get_shipment_by_id,
    update_shipment_part,
    update_shipment,
    delete_shipment as delete_shipment_record,
)
from ..database_orm import get_db
from ..models.shipment_models import Shipment
from ..models.shipment_orm_service import (
    get_shipment_by_id_orm, 
    create_shipment_orm as create_shipment_orm_record,
    update_shipment_part_orm, 
    replace_shipment_full_orm,
    delete_shipment_orm as delete_shipment_orm_record
)
from ..core.dependencies import require_roles, get_current_user
from ..models.users_model import User
from celery.result import AsyncResult
from ..celery.celery_app import celery_app


router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.get("/", response_model = list[ShipmentResponse], status_code = status.HTTP_200_OK)
def list_shipments(
    status: str | None=None, 
    limit: int =10,
):
    shipments = get_all_shipments()
    result =[]
    if status is None:
        return shipments[:limit]
    for shipment in shipments:
        if shipment["status"] == status:
            result.append(shipment)

    return result[:limit]

def _current_customer_id(current_user: User) -> int:
    if current_user.customer is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no customer profile is linked to this account",
        )
    return current_user.customer.id


@router.post("/", response_model = ShipmentResponse, status_code = status.HTTP_201_CREATED)
def create_shipment(
    data: ShipmentCreate,
    current_user: User = Depends(get_current_user),
):
    new_shipment = insert_shipment(
        content=data.content,
        destination=data.destination,
        status=data.status,
        customer_id=_current_customer_id(current_user),
    )
    return new_shipment

@router.get("/orm", response_model=list[ShipmentResponse])
def list_shipments_orm(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if current_user.role in ["admin", "manager"]:
        return db.query(Shipment).all()

    if current_user.customer is None:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No customer profile is linked to this acctount",
        )

    return db.query(Shipment).filter(
        Shipment.customer_id == current_user.customer.id
    ).all()

# @router.get("/", response_model=list[ShipmentResponse])
# def get_shipments(
#     status: str | None = None,
#     destination: str | None = None,
#     limit: int = 10,
#     offset: int = 0,
#     db: Session = Depends(get_db),
# ):
#     return get_all_shipments(
#         db,
#         status=status,
#         destination=destination,
#         limit=limit,
#         offset=offset,
#     )

@router.get("/orm/{shipment_id}", response_model=ShipmentResponse)
def get_shipment_orm_by_id(
    shipment_id:  int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shipment = get_shipment_by_id_orm(db, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code = 404,
            detail = "shipment not found"
        )

    if current_user.role in ["admin", "manager"]:
        return shipment

    if current_user.customer is None:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail = "no customer profile is linked to this account",
        )

    if shipment.customer_id != current_user.customer.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "you do not have permission to view this shipment"
        )

    return shipment

@router.post("/orm", response_model = ShipmentResponse, status_code= status.HTTP_201_CREATED)
def create_shipment_orm(
    data: ShipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shipment = create_shipment_orm_record(
        db,
        data,
        customer_id=_current_customer_id(current_user),
    )

    send_shipment_email.delay(
        recipient_email = current_user.email,
        shipment_id = shipment.id,
        destination = shipment.destination
    )

    return shipment

@router.patch(
        "/orm/{shipment_id}", 
        response_model = ShipmentResponse, 
        status_code = status.HTTP_200_OK,
        dependencies = [Depends(require_roles(["admin"]))]
    )
def modify_shipment_part_orm(
    shipment_id: int,
    shipment_data: ShipmentModify,
    db: Session = Depends(get_db)
):
    updates = shipment_data.model_dump(exclude_unset = True)
    shipment = update_shipment_part_orm(
        db,
        shipment_id,
        updates
    )

    if shipment is None:
        raise HTTPException(
            status_code = 404,
            detail = "shipment is not found"
        )

    return shipment

@router.put(
        "/orm/{shipment_id}", 
        response_model = ShipmentResponse, 
        status_code = status.HTTP_200_OK,
        dependencies = [Depends(require_roles(["admin"]))],
    )
def replace_shipment_orm(
    shipment_id: int,
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db),
):
    shipment = replace_shipment_full_orm(
        db,
        shipment_id,
        shipment_data.model_dump()
    )

    if shipment is None:
        raise HTTPException(
            status_code = 404,
            detail = "shipment not found"
        )

    return shipment

@router.delete(
        "/orm/{shipment_id}", 
        status_code = status.HTTP_204_NO_CONTENT,
        dependencies = [Depends(require_roles(["admin"]))],
    )
def delete_shipment_orm(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_shipment_orm_record(db, shipment_id)
    if not deleted:
        raise HTTPException(
            status_code = 404,
            detail = "shipment not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{shipment_id}")
def get_shipment(shipment_id: int):
    shipment = get_shipment_by_id(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code = 404,
            detail = "shipment not found"
        )

    return shipment

@router.patch("/{shipment_id}", response_model = ShipmentResponse, status_code = status.HTTP_200_OK)
def modify_shipment_part(shipment_id: int, shipment_data: ShipmentModify):
    existing_shipment = get_shipment_by_id(shipment_id)
    if existing_shipment is None:
        raise HTTPException(
            status_code = 404,
            detail="shipment not found"
        )

    updates = shipment_data.model_dump(exclude_unset=True)
    return update_shipment_part(shipment_id, updates)

@router.put("/{shipment_id}", response_model = ShipmentResponse, status_code = status.HTTP_200_OK)
def replace_shipment(shipment_id: int, shipment_data: ShipmentCreate):
    updates = shipment_data.model_dump()
    return update_shipment(shipment_id, updates)


@router.delete("/{shipment_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_shipment(shipment_id: int):
    deleted = delete_shipment_record(shipment_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="shipment not found"
        )

    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.get("/email-tasks/{task_id}")
def get_email_task_status(
    task_id:str,
    current_user: User = Depends(get_current_user)
):
    task = AsyncResult(task_id, app = celery_app)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": (
            str(task.result)
            if task.failed()
            else task.result
            if task.successful()
            else None
        ),
    }


# @router.delete("/{id}")
# def delete_shipment(id: int):
#     for shipment in shipments:
#         if shipment["id"] == id:
#             shipments.remove(shipment)
#             return {"message": "shipment deleted successfully"}

#         raise HTTPException(
#             status_code = 404,
#             detail = "shipment not found"
#         )


# @router.put("/{id}", response_model = ShipmentResponse, status_code = status.HTTP_200_OK)
# def replace_shipment(id: int, data: ShipmentCreate):
#     for shipment in shipments:
#         if shipment["id"] == id:
#                 shipment["content"] = data.content
#                 shipment["status"] = data.status
#                 shipment["destination"] = data.destination
#                 return shipment

#     raise HTTPException(
#         status_code = 404,
#         detail = "shipment id not found"
#     )

# @router.patch("/{id}", response_model = ShipmentResponse, status_code =status.HTTP_200_OK)
# def replace_shipment_part(id: int, data: ShipmentModify):
#     updates = data.model_dump(exclude_unset=True)
#     for shipment in shipments:
#         if shipment["id"] == id:
#             shipment.update(updates)
#             return shipment

#     raise HTTPException(
#         status_code = 404,
#         detail= "shipment not found"
#     )


# @router.get("/{id}")
# def get_shipment(id: int):
#     for shipment in shipments:
#         if shipment["id"] == id:
#             return shipment

#     raise HTTPException(
#         status_code = 404,
#         detail = "shipment not found"
#     )

# @router.post("/", response_model = ShipmentResponse, status_code = status.HTTP_201_CREATED)
# def create_shipment(data: ShipmentCreate):
#     new_shipment = {
#         "id": len(shipments) + 1,
#         "content": data.content,
#         "status": data.status,
#         "destination": data.destination
#     }

#     shipments.append(new_shipment)
#     return new_shipment

# @router.get("/", response_model = list[ShipmentResponse], status_code = status.HTTP_200_OK)
# def get_shipments(status: str | None = None, limit: int = 2):
#     if status is None:
#          return shipments[:limit]

#     result = []
#     for shipment in shipments:
#         if shipment["status"] == status:
#             result.append(shipment)

#     return result[:limit]













