from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..core.security import hash_password, verify_password
from ..models.customer_model import Customer
from ..models.users_model import User


class UserAlreadyExistsError(Exception):
    pass

def create_user(
        db: Session,
        email: str,
        password: str,
        customer_name: str | None = None,
) -> User:
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise UserAlreadyExistsError

    new_user = User(
        email = email,
        hashed_password = hash_password(password),
    )
    new_user.customer = Customer(
        name=customer_name or email.split("@", 1)[0],
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError from exc

    return new_user

def authenticate_user(
        db: Session,
        email: str,
        password: str,
) -> User | None:
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
