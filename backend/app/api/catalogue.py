from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from pathfinder_p4.catalog import card, load, programs
from pathfinder_p4.retrieval import retrieve_evidence

from app.core.security import get_current_user
from app.models.user import User


router = APIRouter(prefix="/catalogue", tags=["P4 catalogue and evidence"])


class CataloguePage(BaseModel):
    total: int
    items: list[dict[str, JsonValue]]


class EvidenceFilters(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    institution_id: str | list[str] | None = None
    program_id: str | list[str] | None = None
    city: str | list[str] | None = None
    sector: str | list[str] | None = None
    field: str | list[str] | None = None
    academic_year: str | list[str] | None = None
    direct_post_bac: bool | list[bool] | None = None
    exploration_visible: bool | list[bool] | None = None
    source_id: str | list[str] | None = None


class EvidenceSearch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)
    filters: EvidenceFilters = Field(default_factory=EvidenceFilters)
    top_k: int = Field(default=5, ge=1, le=50, strict=True)


class EvidenceResult(BaseModel):
    status: Literal["ok", "no_evidence"]
    evidence: list[dict[str, JsonValue]]
    admission_verified: Literal[False] = False


@router.get("/programs", response_model=CataloguePage)
def list_p4_programs(
    city: str | None = None,
    sector: str | None = None,
    field: str | None = None,
    direct_post_bac: bool | None = None,
    include_archive: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    rows = programs(city, sector, field, direct_post_bac, include_archive)
    return {"total": len(rows), "items": rows[offset:offset + limit]}


@router.get("/programs/{program_id}", response_model=dict[str, JsonValue])
def get_p4_program(program_id: str):
    """Return a P4 card with institution, sources, and verification warnings."""
    try:
        return card(program_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="P4 program not found") from error


@router.get("/{resource}", response_model=CataloguePage)
def list_p4_resource(
    resource: Literal["institutions", "careers", "sources", "pathways"],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    rows = load(resource)
    return {"total": len(rows), "items": rows[offset:offset + limit]}


@router.get("/vocabulary/current", response_model=dict[str, JsonValue])
def get_vocabulary():
    """Return P4's versioned draft vocabulary; codes are not admission criteria."""
    return load("vocabulary")


@router.post("/evidence", response_model=EvidenceResult)
async def search_evidence(
    data: EvidenceSearch,
    user: Annotated[User, Depends(get_current_user)],
):
    """Retrieve sourced passages; a retrieval score is not a compatibility score."""
    try:
        evidence = await retrieve_evidence(
            data.query, data.filters.model_dump(exclude_none=True), data.top_k
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Evidence index unavailable; contact the data owner"
        ) from error
    return {"status": "ok" if evidence else "no_evidence", "evidence": evidence}
