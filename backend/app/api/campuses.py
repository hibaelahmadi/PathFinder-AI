from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.campus import Campus
from app.schemas.campus import CampusRead


router = APIRouter(
    prefix="/campuses",
    tags=["Campuses"],
)


@router.get("", response_model=list[CampusRead])
def list_campuses(
    db: Annotated[Session, Depends(get_db)],
    institution_id: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = select(Campus)

    if institution_id is not None:
        statement = statement.where(
            Campus.institution_id == institution_id
        )

    statement = (
        statement
        .order_by(Campus.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{campus_id}", response_model=CampusRead)
def get_campus(
    campus_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    campus = db.get(Campus, campus_id)

    if campus is None:
        raise HTTPException(
            status_code=404,
            detail="Campus not found",
        )

    return campus