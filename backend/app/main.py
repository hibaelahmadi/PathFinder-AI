from typing import Annotated

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import InterfaceError, OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.institutions import router as institutions_router
from app.api.campuses import router as campuses_router
from app.api.programs import router as programs_router
from app.api.careers import router as careers_router
from app.api.admission_criteria import router as admission_criteria_router
from app.api.sources import router as sources_router
from app.api.auth import router as auth_router
from app.api.profiles import router as profiles_router
from app.api.sessions import router as sessions_router
from app.api.recommendations import router as recommendations_router
from app.api.catalogue import router as catalogue_router
from app.core.config import BACKEND_DIR, Settings
from app.db.session import get_db


app = FastAPI(
    title="PathFinder AI API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings().CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(institutions_router)
app.include_router(campuses_router)
app.include_router(programs_router)
app.include_router(careers_router)
app.include_router(admission_criteria_router)
app.include_router(sources_router)
app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(sessions_router)
app.include_router(recommendations_router)
app.include_router(catalogue_router)

EXPECTED_MIGRATION = ScriptDirectory.from_config(
    Config(str(BACKEND_DIR / "alembic.ini"))
).get_current_head()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/ready", response_model=dict[str, str])
def readiness_check(db: Annotated[Session, Depends(get_db)]):
    """Check PostgreSQL access and the applied Alembic migration."""
    revisions = db.scalars(text("SELECT version_num FROM alembic_version")).all()
    if revisions != [EXPECTED_MIGRATION]:
        raise HTTPException(
            status_code=503,
            detail="Database migrations are not current. Run alembic upgrade head.",
        )
    return {"status": "ok", "database": "ok", "migration": EXPECTED_MIGRATION}


@app.exception_handler(OperationalError)
@app.exception_handler(InterfaceError)
async def database_unavailable_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable. Check PostgreSQL and DB_* settings."},
    )


@app.exception_handler(ProgrammingError)
async def database_schema_handler(request: Request, exc: ProgrammingError):
    if getattr(exc.orig, "sqlstate", None) in ("42P01", "42703"):
        return JSONResponse(
            status_code=503,
            content={"detail": "Database schema is not ready. Run alembic upgrade head."},
        )
    return JSONResponse(
        status_code=500, content={"detail": "Database query failed. Contact the backend team."}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = [
        {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )
