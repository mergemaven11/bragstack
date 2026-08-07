from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth_routes import router as auth_router
from app.impact_receipt_routes import router as impact_receipts_router
from app.public_slug_routes import router as public_slug_router
from app.reports_routes import router as reports_router
from app.routes import public_router, router as entries_router


app = FastAPI(
    title="BragStack API",
    description="A SaaS-style tool for tracking career wins, skills, and resume proof.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://congenial-space-orbit-g5pwgj56pg73w7vg-5173.app.github.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(entries_router)
app.include_router(public_router)
app.include_router(public_slug_router)
app.include_router(impact_receipts_router)
app.include_router(reports_router)


@app.get("/")
def root():
    """Return a basic API health check."""
    return {"message": "BragStack API is running"}
