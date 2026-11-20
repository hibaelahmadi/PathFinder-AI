from typing import Literal

from pydantic import BaseModel


class RecommendationConstraints(BaseModel):
    eligibility: Literal["eligible", "ineligible", "unknown"]
    feasibility: Literal["feasible", "not_feasible", "unknown"]
    reasons: list[str]


class RecommendationRead(BaseModel):
    program_id: str
    program_code: str
    program: str
    score: float | None
    explanations: list[str]
    constraints: RecommendationConstraints
    institution_id: str
    institution_name: str | None
    city: str | None
    annual_cost: float | None
    source_id: str
    source_locator: str
    academic_year: str | None
    status: str
    matching_status: str
    admissions_current_verified: bool
    notes: str


class SessionRecommendations(BaseModel):
    session_id: int
    catalogue_kind: Literal["exploration"] = "exploration"
    recommendations: list[RecommendationRead]
    recommendations_total: int
    location_to_verify: list[RecommendationRead]
    location_to_verify_total: int
