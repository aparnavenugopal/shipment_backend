from fastapi.security import OAuth2PasswordBearer
from fastapi import  Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from ..models.users_model import User
from ..database_orm import get_db
from ..core.config import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl = "/users/token"
)

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
)-> User:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms = [settings.jwt_algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError, TypeError) as exc:
        logger.warning("JWT validation failed: %s", type(exc).__name__)
        raise credentials_exception

    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        logger.warning("JWT subject user id %s was not found in the configured database", user_id)
        raise credentials_exception

    return user


def check_role(
    user_role: str,
    allowed_roles: list[str],
) -> None:
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )


def require_roles(allowed_roles: list[str]):
    def role_Checker(
            current_user: User = Depends(get_current_user),
    ) -> User:
        check_role(
            user_role = current_user.role,
            allowed_roles = allowed_roles,
        )
        return current_user

    return role_Checker
