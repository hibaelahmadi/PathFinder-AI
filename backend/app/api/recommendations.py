import json
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from ai.recommendation.adapters import adapt_p4_program, adapt_student_profile
from ai.recommendation.engine import recommend

from app.api.sessions import find_owned_session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import SessionRecommendations


router = APIRouter(prefix="/sessions", tags=["Recommendations"])
DATA = (
    FilePath(__file__).resolve().parents[3]
    / "Pathfinder_P4_Livraison/Pathfinder_P4/data"
)


@router.get("/{session_id}/recommendations", response_model=SessionRecommendations)
def get_session_recommendations(
    session_id: Annotated[int, Path(ge=1, le=2147483647)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    top_n: Annotated[int, Query(ge=1, le=100)] = 5,
):
    session = find_owned_session(db, session_id, user.id)
    if (
        session.status != "completed"
        or not session.profile_confirmed
        or not session.profile
        or session.profile.get("confirme") is not True
    ):
        raise HTTPException(status_code=409, detail="Confirm the questionnaire first")

    try:
        programs = json.loads(
            (DATA / "programs_exploration.json").read_text(encoding="utf-8")
        )
        institutions = json.loads(
            (DATA / "institutions.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Exploration catalogue unavailable"
        ) from error

    institutions_by_id = {item["institution_id"]: item for item in institutions}
    adapted = [
        adapt_p4_program(program, institutions_by_id[program["institution_id"]])
        for program in programs
    ]
    programs_by_id = {program["id"]: program for program in adapted}
    student = adapt_student_profile(session.profile)
    # Rank all candidates before grouping so unknown locations cannot displace
    # the best matching-city results when the student cannot relocate.
    results = recommend(student, adapted, top_n=max(1, len(adapted)))
    recommendations = []
    location_to_verify = []
    for result in results:
        program = programs_by_id[result["program_id"]]
        item = {**program, **result}
        if student["can_relocate"] is False and (
            not student["preferred_city"] or not program["city"]
        ):
            location_to_verify.append(item)
        else:
            recommendations.append(item)

    return {
        "session_id": session_id,
        "recommendations": recommendations[:top_n],
        "recommendations_total": len(recommendations),
        "location_to_verify": location_to_verify[:top_n],
        "location_to_verify_total": len(location_to_verify),
    }
