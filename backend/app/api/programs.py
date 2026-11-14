from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.campus import Campus
from app.models.program import Program
from app.schemas.program import ProgramRead


router = APIRouter(
    prefix="/programs",
    tags=["Programs"],
)


@router.get("", response_model=list[ProgramRead])
def list_programs(
    db: Annotated[Session, Depends(get_db)],
    campus_id: Annotated[int | None, Query(ge=1)] = None,
    institution_id: Annotated[int | None, Query(ge=1)] = None,
    field: Annotated[str | None, Query(min_length=1, max_length=150)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = select(Program)

    if campus_id is not None:
        statement = statement.where(Program.campus_id == campus_id)

    if institution_id is not None:
        statement = statement.join(
            Campus, Program.campus_id == Campus.id
        ).where(Campus.institution_id == institution_id)

    if field is not None:
        statement = statement.where(Program.field == field)

    statement = (
        statement
        .order_by(Program.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{program_id}", response_model=ProgramRead)
def get_program(
    program_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    program = db.get(Program, program_id)

    if program is None:
        raise HTTPException(
            status_code=404,
            detail="Program not found",
        )

    return program