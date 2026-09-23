"""Dashboard summary intelligence metrics."""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.incident import Incident
from backend.models.pattern import SafetyPattern
from backend.models.alert import Alert

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_incidents = db.query(Incident).count()
    active_incidents = db.query(Incident).filter(Incident.status == "active").count()
    patterns = db.query(SafetyPattern).all()
    active_alerts = db.query(Alert).filter(Alert.status == "ACTIVE").count()

    escalating = sum(1 for p in patterns if p.pattern_level == "ESCALATING")
    concerning = sum(1 for p in patterns if p.pattern_level == "CONCERNING")
    emerging = sum(1 for p in patterns if p.pattern_level == "EMERGING")
    normal = sum(1 for p in patterns if p.pattern_level == "NORMAL")

    max_risk = max([p.risk_score for p in patterns], default=0.0)

    return {
        "total_incidents": total_incidents,
        "active_incidents": active_incidents,
        "total_patterns": len(patterns),
        "active_alerts": active_alerts,
        "max_risk_score": max_risk,
        "breakdown": {
            "escalating": escalating,
            "concerning": concerning,
            "emerging": emerging,
            "normal": normal
        }
    }
