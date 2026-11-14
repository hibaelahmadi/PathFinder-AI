from fastapi import FastAPI

from app.api.institutions import router as institutions_router


app = FastAPI(
    title="PathFinder AI API",
    version="0.1.0",
)

app.include_router(institutions_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}