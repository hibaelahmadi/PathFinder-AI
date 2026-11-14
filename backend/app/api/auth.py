from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-only")


@router.post("/register", response_model=UserRead, status_code=201)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    existing = db.scalar(
        select(User).where(func.lower(User.email) == str(data.email))
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        email=str(data.email),
        hashed_password=hash_password(data.password.get_secret_value()),
        role="student",
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        if getattr(error.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            ) from error

        raise

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.scalar(
        select(User).where(func.lower(User.email) == str(data.email))
    )

    stored_hash = (
        user.hashed_password if user is not None else DUMMY_PASSWORD_HASH
    )
    password_matches = verify_password(
        data.password.get_secret_value(),
        stored_hash,
    )

    if user is None or not password_matches or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )


@router.get("/me", response_model=UserRead)
def get_me(
    user: Annotated[User, Depends(get_current_user)],
):
    return user