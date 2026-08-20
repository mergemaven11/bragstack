from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth_routes import router as auth_router
from app.certification_packet_export_routes import router as certification_packet_export_router
from app.certification_packet_routes import router as certification_packet_router
from app.impact_receipt_routes import router as impact_receipts_router
from app.interview_packet_export_routes import router as interview_packet_export_router
from app.interview_packet_routes import router as interview_packet_router
from app.packet_audit_routes import router as packet_audit_router
from app.packet_platform_export_routes import router as packet_platform_export_router
from app.packet_platform_routes import router as packet_platform_router
from app.packet_share_routes import router as packet_share_router
from app.performance_packet_export_routes import router as performance_packet_export_router
from app.performance_packet_routes import router as performance_packet_router
from app.promotion_packet_export_routes import router as promotion_packet_export_router
from app.promotion_packet_routes import router as promotion_packet_router
from app.public_slug_routes import router as public_slug_router
from app.reports_routes import router as reports_router
from app.routes import public_router, router as entries_router


app = FastAPI(
    title="BragStack API",
    description="Evidence-backed career proof for accomplishments, impact, and reports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.app\.github\.dev",
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
app.include_router(performance_packet_router)
app.include_router(performance_packet_export_router)
app.include_router(packet_platform_router)
app.include_router(packet_platform_export_router)
app.include_router(packet_audit_router)
app.include_router(packet_share_router)
app.include_router(promotion_packet_router)
app.include_router(promotion_packet_export_router)
app.include_router(interview_packet_router)
app.include_router(interview_packet_export_router)
app.include_router(certification_packet_router)
app.include_router(certification_packet_export_router)


@app.get("/")
def root():
    """Return a basic API health check."""
    return {"message": "BragStack API is running"}
