from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathfinder_p4.catalog import load

from ai.chatbot.questionnaire import (
    creer_profil,
    prochaine_question,
    traiter_questionnaire,
)

from app.core.security import get_current_user
from app.core.config import Settings
from app.db.session import get_db
from app.models.questionnaire_answer import QuestionnaireAnswer
from app.models.questionnaire_session import QuestionnaireSession
from app.models.user import User
from app.schemas.questionnaire import (
    QuestionnaireAnswerRead,
    QuestionnaireAction,
    QuestionnaireResult,
    QuestionnaireSessionRead,
)


router = APIRouter(prefix="/sessions", tags=["Questionnaire sessions"])
settings = Settings()


def find_owned_session(
    db: Session,
    session_id: int,
    user_id: int,
    for_update: bool = False,
) -> QuestionnaireSession:
    statement = select(QuestionnaireSession).where(
        QuestionnaireSession.id == session_id,
        QuestionnaireSession.user_id == user_id,
    )
    if for_update:
        statement = statement.with_for_update().execution_options(
            populate_existing=True
        )
    session = db.scalar(statement)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Questionnaire session not found",
        )

    return session


def load_questionnaire_state(db: Session, session: QuestionnaireSession):
    stored_answers = {
        answer.question_code: answer
        for answer in db.scalars(
            select(QuestionnaireAnswer).where(
                QuestionnaireAnswer.session_id == session.id
            )
        ).all()
    }
    state = {
        "status": session.status,
        "expected_question_code": session.expected_question_code,
        "answers": {
            code: {
                "question_code": code,
                "question_text": answer.question_text,
                "answer_text": answer.answer_text,
                "answer_value": answer.answer_value,
            }
            for code, answer in stored_answers.items()
        },
    }
    return state, stored_answers


@router.post("", response_model=QuestionnaireSessionRead, status_code=201)
def create_session(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    categories = load("vocabulary")["categories"]
    options = {
        "inclure_budget_type": True,
        "matieres": categories["required_subjects"],
        "codes_interets": categories["interests"],
        "codes_competences": categories["skills"],
        "codes_metiers": categories["career_paths"],
    }
    result = QuestionnaireResult.model_validate(
        traiter_questionnaire(None, "start", **options)
    )
    if result.errors:
        raise HTTPException(status_code=422, detail=result.errors)

    session = QuestionnaireSession(
        user_id=user.id,
        status=result.etat.status,
        expected_question_code=result.etat.expected_question_code,
        next_question=result.next_question.model_dump() if result.next_question else None,
        questionnaire_options=options,
        profile=result.profile,
        profile_confirmed=result.profile_confirmed,
    )
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


@router.post("/{session_id}/actions", response_model=QuestionnaireResult)
def process_questionnaire_action(
    session_id: Annotated[int, Path(ge=1, le=2147483647)],
    data: QuestionnaireAction,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    try:
        session = find_owned_session(db, session_id, user.id, for_update=True)
        state, stored_answers = load_questionnaire_state(db, session)
        result = QuestionnaireResult.model_validate(
            traiter_questionnaire(
                state,
                data.action,
                data.reponse.model_dump() if data.reponse is not None else None,
                **session.questionnaire_options,
                enrichir_profil=settings.QUESTIONNAIRE_ENRICH_PROFILE,
            )
        )
        if result.errors:
            raise HTTPException(status_code=422, detail=result.errors)

        for code in result.answer_codes_to_delete:
            answer = stored_answers.pop(code, None)
            if answer is not None:
                db.delete(answer)

        for accepted in result.answers_to_save:
            answer = stored_answers.get(accepted.question_code)
            if answer is None:
                answer = QuestionnaireAnswer(
                    session_id=session_id,
                    question_code=accepted.question_code,
                )
                db.add(answer)
            answer.question_text = accepted.question_text
            answer.answer_text = accepted.answer_text
            answer.answer_value = accepted.answer_value

        session.status = result.etat.status
        session.expected_question_code = result.etat.expected_question_code
        session.next_question = (
            result.next_question.model_dump() if result.next_question else None
        )
        session.profile = result.profile
        session.profile_confirmed = result.profile_confirmed
        db.commit()
    except Exception:
        db.rollback()
        raise

    return result


@router.get("/{session_id}/state", response_model=QuestionnaireResult)
def get_questionnaire_state(
    session_id: Annotated[int, Path(ge=1, le=2147483647)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    try:
        session = find_owned_session(db, session_id, user.id, for_update=True)
        state, stored_answers = load_questionnaire_state(db, session)
        question = session.next_question
        # Sessions created before the context migration have no saved question.
        if not session.questionnaire_options and session.status == "in_progress":
            question = prochaine_question({
                code: answer.answer_value
                for code, answer in stored_answers.items()
            })
        if session.status == "completed":
            question = None
        state["expected_question_code"] = (
            question["question_code"] if question else None
        )
        result = QuestionnaireResult.model_validate({
            "etat": state,
            "next_question": question,
            "answers_to_save": [],
            "answer_codes_to_delete": [],
            "profile": (
                session.profile if session.profile is not None else creer_profil()
            ),
            "profile_confirmed": session.profile_confirmed,
            "errors": [],
        })
    finally:
        db.rollback()

    return result


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
