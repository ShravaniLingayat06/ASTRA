from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    incident_type: str = Field(..., example="harassment")
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    reporter_type: str = Field("citizen", example="citizen")
    source: str = Field("manual", example="manual")
    severity: int = Field(3, ge=1, le=5)

class IncidentCreate(IncidentBase):
    timestamp: Optional[datetime] = None

class IncidentOut(IncidentBase):
    id: str
    timestamp: datetime
    reporter_id: Optional[str] = None
    status: str
    duplicate_candidate: bool
    cluster_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
