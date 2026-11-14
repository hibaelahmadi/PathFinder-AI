from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models.institution import Institution


@pytest.mark.parametrize(
    "query",
    [
        "?offset=-1",
        "?limit=0",
        "?limit=101",
        "?limit=abc",
    ],
)
def test_institutions_rejects_invalid_pagination(query):
    def override_get_db():
        yield None

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get(f"/institutions{query}")
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 422


def test_institutions_returns_paginated_records(db_connection):
    suffix = uuid4().hex
    records = []

    for index in range(3):
        institution_id = db_connection.execute(
            insert(Institution)
            .values(
                code=f"api-test-{suffix}-{index}",
                name=f"Test institution {index}",
                type="public",
                website=None,
            )
            .returning(Institution.id)
        ).scalar_one()

        records.append(
            {
                "id": institution_id,
                "code": f"api-test-{suffix}-{index}",
                "name": f"Test institution {index}",
                "type": "public",
                "website": None,
            }
        )

    target = records[1]

    offset = db_connection.execute(
        select(func.count())
        .select_from(Institution)
        .where(Institution.id < target["id"])
    ).scalar_one()

    def override_get_db():
        with Session(
            bind=db_connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get(
                "/institutions",
                params={"offset": offset, "limit": 1},
            )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 200
    assert response.json() == [target]

@pytest.mark.parametrize("institution_id", ["0", "-1", "abc"])
def test_institution_rejects_invalid_id(institution_id):
    def override_get_db():
        yield None

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get(f"/institutions/{institution_id}")
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 422