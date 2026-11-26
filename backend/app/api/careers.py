from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.career import Career
from app.models.program_career import ProgramCareer
from app.schemas.career import CareerRead


router = APIRouter(
    prefix="/careers",
    tags=["Careers"],
)


@router.get("", response_model=list[CareerRead])
def list_careers(
    db: Annotated[Session, Depends(get_db)],
    program_id: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = select(Career)

    if program_id is not None:
        statement = statement.join(
            ProgramCareer,
            Career.id == ProgramCareer.career_id,
        ).where(ProgramCareer.program_id == program_id)

    statement = (
        statement
        .order_by(Career.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{career_id}", response_model=CareerRead)
def get_career(
    career_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    career = db.get(Career, career_id)

    if career is None:
        raise HTTPException(
            status_code=404,
            detail="Career not found",
        )

    return career