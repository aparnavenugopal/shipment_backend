from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models.customer_model import Customer
from ..models.users_model import User
from ..model import CustomerCreate, CustomerModify

class CustomerUserNotFoundError(Exception):
    pass

class CustomerAlreadyLinkedError(Exception):
    pass


def _validate_user_link(
        db: Session,
        user_id: int,
        customer_id: int | None = None,
) -> User:
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise CustomerUserNotFoundError

    statement = select(Customer).where(Customer.user_id == user_id)
    if customer_id is not None:
        statement = statement.where(Customer.id != customer_id)
    linked_customer = db.scalar(statement)
    if linked_customer is not None:
        raise CustomerAlreadyLinkedError

    return user


def insert_customer(
        db: Session,
        customer_data: CustomerCreate,
) -> Customer:
    user = _validate_user_link(db, customer_data.user_id)
    customer = Customer(
        name = customer_data.name,
        user = user,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer

def list_all_customers(db: Session)-> list[Customer]:
    return db.query(Customer).all()

def fetch_customer_by_id(
        db: Session,
        customer_id: int
) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()

def modify_customer_part(
        db: Session,
        customer_id: int,
        customer_data: CustomerModify
) -> Customer | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        return None

    update_data = customer_data.model_dump(exclude_unset=True)

    if update_data.get("user_id") is not None:
        user = _validate_user_link(
            db,
            update_data["user_id"],
            customer_id=customer.id,
        )
        update_data["user"] = user
        del update_data["user_id"]

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer

def update_customer(
        db: Session,
        customer_id: int,
        customer_data: CustomerCreate
) -> Customer | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        return None

    customer.name = customer_data.name
    if customer_data.user_id is not None:
        customer.user = _validate_user_link(
            db,
            customer_data.user_id,
            customer_id=customer.id,
        )

    db.commit()
    db.refresh(customer)

    return customer

def delete_customer(
        db: Session,
        customer_id: int
) -> bool:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        return False

    db.delete(customer)
    db.commit()

    return True
