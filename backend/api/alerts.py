"""Alerts API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.alert import AlertOut, AlertUpdate
from backend.services.alert_service import get_alerts, update_alert_status

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertOut])
def list_alerts(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve explainable security alerts."""
    return get_alerts(db, status=status)

@router.patch("/{alert_id}", response_model=AlertOut)
def modify_alert_status(alert_id: str, update_in: AlertUpdate, db: Session = Depends(get_db)):
    alert = update_alert_status(db, alert_id, update_in.status)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
