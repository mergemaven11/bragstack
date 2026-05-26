from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BragEntryCreate(BaseModel):
    """Request model for creating a brag entry."""

    title: str = Field(..., examples=["Debugged Docker networking issue"])
    category: str = Field(..., examples=["Docker"])
    situation: str = Field(..., examples=["Customer container could not connect to MongoDB."])
    action: str = Field(..., examples=["Checked logs, inspected networks, and verified Compose service names."])
    impact: str = Field(..., examples=["Found incorrect hostname and restored connectivity."])
    lesson: Optional[str] = Field(None, examples=["Docker Compose DNS uses service names."])
    tags: list[str] = Field(default_factory=list, examples=[["Docker", "Networking", "Compose"]])


class BragEntryResponse(BaseModel):
    """Response model for a brag entry."""

    id: str
    title: str
    category: str
    situation: str
    action: str
    impact: str
    lesson: Optional[str]
    tags: list[str]
    resume_bullet: str
    created_at: datetime