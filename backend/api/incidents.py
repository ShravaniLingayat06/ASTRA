"""Incident reporting and ingestion API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.incident import IncidentCreate, IncidentOut
from backend.services.incident_service import create_incident, get_incidents
from backend.services.pattern_service import refresh_safety_patterns
from backend.security.auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("/", response_model=IncidentOut)
def report_incident(
    inc_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Ingest a safety incident. Open to citizen submissions and CV automated signals.
    Triggers clustering re-evaluation in real-time.
    """
    reporter_id = current_user.id if current_user else None
    inc = create_incident(db, inc_in, reporter_id=reporter_id)
    
    # Refresh patterns immediately to connect the dots
    try:
        refresh_safety_patterns(db)
    except Exception as e:
        print(f"Pattern refresh warning: {e}")
        
    return inc

@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_incidents(db, skip=skip, limit=limit, status=status)
