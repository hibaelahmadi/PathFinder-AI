from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.admission_criterion_source import AdmissionCriterionSource
from app.models.program_source import ProgramSource
from app.models.source import Source
from app.schemas.source import SourceRead


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.get("", response_model=list[SourceRead])
def list_sources(
    db: Annotated[Session, Depends(get_db)],
    program_id: Annotated[int | None, Query(ge=1)] = None,
    criterion_id: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = select(Source)

    if program_id is not None:
        statement = statement.join(
            ProgramSource,
            Source.id == ProgramSource.source_id,
        ).where(ProgramSource.program_id == program_id)

    if criterion_id is not None:
        statement = statement.join(
            AdmissionCriterionSource,
            Source.id == AdmissionCriterionSource.source_id,
        ).where(
            AdmissionCriterionSource.admission_criterion_id == criterion_id
        )

    statement = (
        statement
        .order_by(Source.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{source_id}", response_model=SourceRead)
def get_source(
    source_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    source = db.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    return source