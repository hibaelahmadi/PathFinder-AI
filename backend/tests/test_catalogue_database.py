from uuid import uuid4
from datetime import date

import pytest
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from app.models.institution import Institution
from app.models.campus import Campus
from app.models.program import Program
from app.models.source import Source
from app.models.admission_criterion_source import AdmissionCriterionSource


from app.models.admission_criterion import AdmissionCriterion


def test_program_rejects_negative_cost(db_connection):
    suffix = uuid4().hex

    institution_id = db_connection.execute(
        insert(Institution)
        .values(
            code=f"test-institution-{suffix}",
            name="Test institution",
        )
        .returning(Institution.id)
    ).scalar_one()

    campus_id = db_connection.execute(
        insert(Campus)
        .values(
            code=f"test-campus-{suffix}",
            institution_id=institution_id,
            name="Test campus",
            city="Rabat",
        )
        .returning(Campus.id)
    ).scalar_one()

    with pytest.raises(IntegrityError) as error:
        with db_connection.begin_nested():
            db_connection.execute(
                insert(Program).values(
                    code=f"test-program-{suffix}",
                    campus_id=campus_id,
                    name="Test program",
                    annual_cost=-1,
                )
            )

    assert error.value.orig.diag.constraint_name == (
        "ck_programs_annual_cost_nonnegative"
    )


def test_admission_rejects_deadline_before_opening(db_connection):
    suffix = uuid4().hex

    institution_id = db_connection.execute(
        insert(Institution)
        .values(
            code=f"test-institution-{suffix}",
            name="Test institution",
        )
        .returning(Institution.id)
    ).scalar_one()

    campus_id = db_connection.execute(
        insert(Campus)
        .values(
            code=f"test-campus-{suffix}",
            institution_id=institution_id,
            name="Test campus",
            city="Rabat",
        )
        .returning(Campus.id)
    ).scalar_one()

    program_id = db_connection.execute(
        insert(Program)
        .values(
            code=f"test-program-{suffix}",
            campus_id=campus_id,
            name="Test program",
        )
        .returning(Program.id)
    ).scalar_one()

    with pytest.raises(IntegrityError) as error:
        with db_connection.begin_nested():
            db_connection.execute(
                insert(AdmissionCriterion).values(
                    code=f"test-admission-{suffix}",
                    program_id=program_id,
                    academic_year="2026-2027",
                    campaign="main",
                    official_text="Fictional test conditions.",
                    application_opens=date(2026, 6, 10),
                    application_deadline=date(2026, 6, 1),
                )
            )

    assert error.value.orig.diag.constraint_name == (
        "ck_admission_application_dates"
    )

def test_campus_rejects_missing_institution(db_connection):
    suffix = uuid4().hex

    institution_id = db_connection.execute(
        insert(Institution)
        .values(
            code=f"test-institution-{suffix}",
            name="Temporary institution",
        )
        .returning(Institution.id)
    ).scalar_one()

    db_connection.execute(
        Institution.__table__.delete().where(
            Institution.id == institution_id
        )
    )

    with pytest.raises(IntegrityError) as error:
        with db_connection.begin_nested():
            db_connection.execute(
                insert(Campus).values(
                    code=f"test-campus-{suffix}",
                    institution_id=institution_id,
                    name="Test campus",
                    city="Rabat",
                )
            )

    assert error.value.orig.sqlstate == "23503"

def test_admission_source_rejects_duplicate_link(db_connection):
    suffix = uuid4().hex

    institution_id = db_connection.execute(
        insert(Institution)
        .values(code=f"inst-{suffix}", name="Test institution")
        .returning(Institution.id)
    ).scalar_one()

    campus_id = db_connection.execute(
        insert(Campus)
        .values(
            code=f"campus-{suffix}",
            institution_id=institution_id,
            name="Test campus",
            city="Rabat",
        )
        .returning(Campus.id)
    ).scalar_one()

    program_id = db_connection.execute(
        insert(Program)
        .values(
            code=f"program-{suffix}",
            campus_id=campus_id,
            name="Test program",
        )
        .returning(Program.id)
    ).scalar_one()

    admission_id = db_connection.execute(
        insert(AdmissionCriterion)
        .values(
            code=f"admission-{suffix}",
            program_id=program_id,
            academic_year="2026-2027",
            campaign="main",
            official_text="Fictional test conditions.",
        )
        .returning(AdmissionCriterion.id)
    ).scalar_one()

    source_id = db_connection.execute(
        insert(Source)
        .values(
            code=f"source-{suffix}",
            url="https://example.org/test",
            title="Fictional test source",
            retrieved_at=date(2026, 11, 14),
        )
        .returning(Source.id)
    ).scalar_one()

    link = insert(AdmissionCriterionSource).values(
        admission_criterion_id=admission_id,
        source_id=source_id,
    )

    db_connection.execute(link)

    with pytest.raises(IntegrityError) as error:
        with db_connection.begin_nested():
            db_connection.execute(link)

    assert error.value.orig.sqlstate == "23505"
    assert error.value.orig.diag.constraint_name == (
        "admission_criterion_sources_pkey"
    )