from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.student_profile import (
    StudentProfileRead,
    StudentProfileUpdate,
)


router = APIRouter(prefix="/profiles", tags=["Student profiles"])


@router.get("/me", response_model=StudentProfileRead)
def get_my_profile(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    profile = db.get(StudentProfile, user.id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found",
        )

    return profile


@router.patch("/me", response_model=StudentProfileRead)
def update_my_profile(
    data: StudentProfileUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    profile = db.get(StudentProfile, user.id)

    if profile is None:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        if getattr(error.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail="Profile changed concurrently; retry the request",
            ) from error

        raise

    db.refresh(profile)
    return profile