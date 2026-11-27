from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


settings = Settings()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

connect_args: dict[str, int | str] = {"connect_timeout": 5}
if settings.DB_SSLMODE is not None:
    connect_args["sslmode"] = settings.DB_SSLMODE
if settings.DB_SSLROOTCERT is not None:
    connect_args["sslrootcert"] = settings.DB_SSLROOTCERT

engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
