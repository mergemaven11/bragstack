from fastapi import FastAPI

from app.routes import router as entries_router


app = FastAPI(
    title="BragStack API",
    description="A SaaS-style tool for tracking career wins, skills, and resume proof.",
    version="0.1.0",
)


@app.get("/")
def root():
    """Return API health status."""
    return {
        "status": "ok",
        "message": "BragStack API is running",
    }


app.include_router(entries_router)