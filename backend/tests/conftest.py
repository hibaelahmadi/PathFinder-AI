import os

import pytest
from sqlalchemy import URL, create_engine, text


@pytest.fixture
def db_connection():
    if os.environ.get("RUN_DB_TESTS") != "1":
        pytest.skip("Set RUN_DB_TESTS=1 to run PostgreSQL tests.")

    from app.core.config import Settings

    settings = Settings()

    url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database="pathfinder_test_db",
    )

    engine = create_engine(url)

    try:
        with engine.connect() as connection:
            actual_database = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()
            connection.rollback()

            if actual_database != "pathfinder_test_db":
                pytest.fail("Database tests require pathfinder_test_db.")

            transaction = connection.begin()

            try:
                yield connection
            finally:
                transaction.rollback()
    finally:
        engine.dispose()