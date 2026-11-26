from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.admission_criterion import AdmissionCriterion
from app.schemas.admission_criterion import AdmissionCriterionRead


router = APIRouter(
    prefix="/admission-criteria",
    tags=["Admission criteria"],
)


@router.get("", response_model=list[AdmissionCriterionRead])
def list_admission_criteria(
    db: Annotated[Session, Depends(get_db)],
    program_id: Annotated[int | None, Query(ge=1)] = None,
    academic_year: Annotated[
        str | None,
        Query(pattern=r"^\d{4}-\d{4}$"),
    ] = None,
    campaign: Annotated[
        str | None,
        Query(min_length=1, max_length=100),
    ] = None,
    verification_status: Literal["unverified", "verified"] | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = select(AdmissionCriterion)

    if program_id is not None:
        statement = statement.where(
            AdmissionCriterion.program_id == program_id
        )

    if academic_year is not None:
        statement = statement.where(
            AdmissionCriterion.academic_year == academic_year
        )

    if campaign is not None:
        statement = statement.where(
            AdmissionCriterion.campaign == campaign
        )

    if verification_status is not None:
        statement = statement.where(
            AdmissionCriterion.verification_status == verification_status
        )

    statement = (
        statement
        .order_by(AdmissionCriterion.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{criterion_id}", response_model=AdmissionCriterionRead)
def get_admission_criterion(
    criterion_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    criterion = db.get(AdmissionCriterion, criterion_id)

    if criterion is None:
        raise HTTPException(
            status_code=404,
            detail="Admission criteria not found",
        )

    return criterion