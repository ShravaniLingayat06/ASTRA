"""Service layer for incident ingestion, deduplication, and lookup."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.incident import Incident
from backend.schemas.incident import IncidentCreate
from backend.analytics.duplicate_detection import detect_duplicates
from backend.analytics.anti_gaming import check_anti_gaming

def create_incident(db: Session, inc_in: IncidentCreate, reporter_id: Optional[str] = None) -> Incident:
    timestamp = inc_in.timestamp or datetime.now(timezone.utc)
    
    # Anti-gaming check if reporter_id provided
    if reporter_id:
        user_incidents = [
            {"latitude": i.latitude, "longitude": i.longitude, "created_at": i.created_at}
            for i in db.query(Incident).filter(Incident.reporter_id == reporter_id).all()
        ]
        anti_res = check_anti_gaming(user_incidents)
        if anti_res["flagged"]:
            pass  # Could flag or throttle, still record with audit tag

    new_inc = Incident(
        incident_type=inc_in.incident_type,
        description=inc_in.description,
        latitude=inc_in.latitude,
        longitude=inc_in.longitude,
        timestamp=timestamp,
        reporter_id=reporter_id,
        reporter_type=inc_in.reporter_type,
        source=inc_in.source,
        severity=inc_in.severity,
        status="active"
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)

    # Check for near-duplicate candidates
    recent_active = db.query(Incident).filter(Incident.status == "active").all()
    inc_dicts = [
        {"id": i.id, "latitude": i.latitude, "longitude": i.longitude,
         "timestamp": i.timestamp, "incident_type": i.incident_type}
        for i in recent_active
    ]
    dupes = detect_duplicates(inc_dicts)
    for pair in dupes:
        id1 = pair["incident_id_1"] if isinstance(pair, dict) else pair[0]
        id2 = pair["incident_id_2"] if isinstance(pair, dict) else pair[1]
        if new_inc.id in (id1, id2):
            new_inc.duplicate_candidate = True
            db.commit()
            break

    return new_inc

def get_incidents(db: Session, skip: int = 0, limit: int = 200, status: Optional[str] = None) -> List[Incident]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(Incident.timestamp.desc()).offset(skip).limit(limit).all()
