from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from urllib.parse import parse_qs
from ..core.security import create_access_token
from ..services.user_service import UserAlreadyExistsError, authenticate_user, create_user
from ..database_orm import get_db
from ..model import TokenResponse, UserCreate, UserLogin, UserResponse
from ..core.rate_limiter import limiter

router = APIRouter(prefix = "/users", tags = ["Users"])


def _create_token_for_credentials(
    db: Session,
    email: str,
    password: str,
) -> dict[str, str]:
    user = authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

@router.post(
    "/register",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
)
@limiter.limit("20/hour")
def register_user(
    request: Request,
    data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_user(
            db = db,
            email = str(data.email),
            password = data.password,
            customer_name = data.customer_name,
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Email is already registered",
        )

@router.post(
    "/login",
    response_model = TokenResponse,
    status_code = status.HTTP_200_OK
)
@limiter.limit("20/minute")
def login_user(
    data: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    return _create_token_for_credentials(
        db=db,
        email=str(data.email),
        password=data.password,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("20/minute")
async def issue_oauth_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="OAuth token requests must use application/x-www-form-urlencoded",
        )

    try:
        form = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid form encoding",
        ) from exc

    username = form.get("username", [""])[0]
    password = form.get("password", [""])[0]
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username and password are required",
        )

    return _create_token_for_credentials(
        db=db,
        email=username,
        password=password,
    )

    
