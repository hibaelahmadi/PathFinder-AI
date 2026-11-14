from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.questionnaire_answer import QuestionnaireAnswer
from app.models.questionnaire_session import QuestionnaireSession
from app.models.user import User
from app.schemas.questionnaire import (
    QuestionnaireAnswerRead,
    QuestionnaireSessionRead,
)


router = APIRouter(prefix="/sessions", tags=["Questionnaire sessions"])


def find_owned_session(
    db: Session,
    session_id: int,
    user_id: int,
) -> QuestionnaireSession:
    session = db.scalar(
        select(QuestionnaireSession).where(
            QuestionnaireSession.id == session_id,
            QuestionnaireSession.user_id == user_id,
        )
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Questionnaire session not found",
        )

    return session


@router.post("", response_model=QuestionnaireSessionRead, status_code=201)
def create_session(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    session = QuestionnaireSession(user_id=user.id)
    db.add(session)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(session)
    return session


@router.get("", response_model=list[QuestionnaireSessionRead])
def list_sessions(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = (
        select(QuestionnaireSession)
        .where(QuestionnaireSession.user_id == user.id)
        .order_by(QuestionnaireSession.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{session_id}", response_model=QuestionnaireSessionRead)
def get_session(
    session_id: Annotated[int, Path(ge=1, le=2147483647)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return find_owned_session(db, session_id, user.id)


@router.get(
    "/{session_id}/answers",
    response_model=list[QuestionnaireAnswerRead],
)
def list_answers(
    session_id: Annotated[int, Path(ge=1, le=2147483647)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    find_owned_session(db, session_id, user.id)

    statement = (
        select(QuestionnaireAnswer)
        .where(QuestionnaireAnswer.session_id == session_id)
        .order_by(QuestionnaireAnswer.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()