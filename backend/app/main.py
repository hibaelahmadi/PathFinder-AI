from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.institutions import router as institutions_router
from app.api.campuses import router as campuses_router
from app.api.programs import router as programs_router
from app.api.careers import router as careers_router
from app.api.admission_criteria import router as admission_criteria_router
from app.api.sources import router as sources_router
from app.api.auth import router as auth_router
from app.api.profiles import router as profiles_router


app = FastAPI(
    title="PathFinder AI API",
    version="0.1.0",
)

app.include_router(institutions_router)
app.include_router(campuses_router)
app.include_router(programs_router)
app.include_router(careers_router)
app.include_router(admission_criteria_router)
app.include_router(sources_router)
app.include_router(auth_router)
app.include_router(profiles_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


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
