from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AlertOut(BaseModel):
    id: str
    pattern_id: Optional[str] = None
    alert_level: str
    risk_score: float
    headline: str
    explanation: str
    recommended_action: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: str
