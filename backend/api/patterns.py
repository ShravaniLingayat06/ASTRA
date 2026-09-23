"""Pattern intelligence API routes."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.pattern import PatternOut
from backend.services.pattern_service import get_patterns, refresh_safety_patterns

router = APIRouter(prefix="/patterns", tags=["patterns"])

@router.get("/", response_model=List[PatternOut])
def list_patterns(db: Session = Depends(get_db)):
    """Retrieve all detected safety patterns ranked by risk score."""
    return get_patterns(db)

@router.post("/refresh", response_model=List[PatternOut])
def trigger_refresh(db: Session = Depends(get_db)):
    """Manually trigger multi-signal clustering and pattern recalculation."""
    return refresh_safety_patterns(db)
