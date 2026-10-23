from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..model import ShipmentCreate
from .shipment_models import Shipment
from .customer_model import Customer  # noqa: F401 - registers the relationship target

def get_all_shipments(db: Session) -> list[Shipment]:
    statement = select(Shipment).options(
        joinedload(Shipment.customer)
    )

    return db.scalars(statement).all()

# def get_all_shipments(
#     db: Session,
#     status: str | None = None,
#     destination: str | None = None,
#     limit: int = 10,
#     offset: int = 0,
# ) -> list[Shipment]:

#     statement = select(Shipment).options(
#         joinedload(Shipment.customer)
#     )

#     if status is not None:
#         statement = statement.where(Shipment.status == status)

#     if destination is not None:
#         statement = statement.where(
#             Shipment.destination == destination
#         )

#     statement = (
#         statement
#         .order_by(Shipment.id)
#         .limit(limit)
#         .offset(offset)
#     )

#     return db.scalars(statement).all()

def get_shipment_by_id_orm(
        db: Session,
        shipment_id: int,
):
    return(
        db.query(Shipment)
        .options(joinedload(Shipment.customer))
        .filter(Shipment.id == shipment_id)
        .first()
    )

def create_shipment_orm(
        db: Session,
        data: ShipmentCreate,
        customer_id: int,
) -> Shipment:
    shipment = Shipment(
        content = data.content,
        destination = data.destination,
        status = data.status,
        customer_id = customer_id
    )

    try:
        db.add(shipment)
        db.commit()
        db.refresh(shipment)
        return (
            db.query(Shipment)
            .options(joinedload(Shipment.customer))
            .filter(Shipment.id == shipment.id)
            .one()
        )

    except Exception:
        db.rollback()
        raise

def update_shipment_part_orm(
        db: Session,
        shipment_id: int,
        updates: dict,
):
    shipment = (
        db.query(Shipment)
        .filter(Shipment.id == shipment_id)
        .first()

    )
    if shipment is None:
        return None

    for field, value in updates.items():
        setattr(shipment, field, value)

    try:
        db.commit()
        db.refresh(shipment)
        return shipment
    except Exception:
        db.rollback()
        raise

def replace_shipment_full_orm(
        db: Session,
        shipment_id: int,
        data: dict
):
    shipment = (
        db.query(Shipment)
        .filter(Shipment.id == shipment_id)
        .first()
    )

    if shipment is None:
        return None

    for field,value in data.items():
        setattr(shipment, field, value)

    try:
        db.commit()
        db.refresh(shipment)
        return shipment

    except Exception:
        db.rollback()
        raise

def delete_shipment_orm(
        db: Session,
        shipment_id: int,
) -> bool:
    shipment = (
        db.query(Shipment)
        .filter(Shipment.id == shipment_id)
        .first()
    )

    if shipment is None:
        return False

    try:
        db.delete(shipment)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


