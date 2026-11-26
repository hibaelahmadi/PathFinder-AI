from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator


class RecommendationProfile(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)

    bac: str | None = None
    code_bac: str | None = None
    ville_souhaitee: str | None = None
    mobilite: Literal["oui", "non", "je ne sais pas"] | None = None
    notes: dict[str, Annotated[float, Field(ge=0, le=20, allow_inf_nan=False)]] | None = None
    budget_annuel_max: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None = None
    type_etablissement: Literal["public", "prive"] | None = None
    categories_interets: list[str] | None = None
    categories_competences: list[str] | None = None
    code_metier: str | None = None

    @model_validator(mode="after")
    def validate_codes(self, info: ValidationInfo):
        categories = info.context["categories"]
        fields = {
            "code_bac": "accepted_bac_types",
            "categories_interets": "interests",
            "categories_competences": "skills",
            "code_metier": "career_paths",
            "notes": "required_subjects",
        }
        for name, vocabulary in fields.items():
            value = getattr(self, name)
            if value is None:
                continue
            codes = [value] if isinstance(value, str) else value
            if set(codes) - set(categories[vocabulary]):
                raise ValueError(f"Unknown vocabulary code in {name}")
        return self


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
