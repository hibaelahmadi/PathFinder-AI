from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionRead


router = APIRouter(
    prefix="/institutions",
    tags=["Institutions"],
)


@router.get("", response_model=list[InstitutionRead])
def list_institutions(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = (
        select(Institution)
        .order_by(Institution.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{institution_id}", response_model=InstitutionRead)
def get_institution(
    institution_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    institution = db.get(Institution, institution_id)

    if institution is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    return institution