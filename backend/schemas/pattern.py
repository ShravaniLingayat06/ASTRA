from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PatternOut(BaseModel):
    id: str
    cluster_id: Optional[int] = None
    title: Optional[str] = None
    incident_count: int
    incident_types: Optional[List[str]] = None
    incident_ids: Optional[List[str]] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: float = 150.0
    time_window: Optional[str] = None
    reporter_diversity: int = 1
    trend_score: float = 0.0
    risk_score: float = 0.0
    pattern_level: str = "NORMAL"
    status: str = "NEW"
    explanation: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
