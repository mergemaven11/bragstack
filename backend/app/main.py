from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth_routes import router as auth_router
from app.routes import router as entries_router

app = FastAPI(
    title="BragStack API",
    description="A SaaS-style tool for tracking career wins, skills, and resume proof.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(entries_router)


@app.get("/")
def root():
    """Return a basic API health check.

    Returns:
        A dictionary confirming that the API is running.
    """
    return {"message": "BragStack API is running"}