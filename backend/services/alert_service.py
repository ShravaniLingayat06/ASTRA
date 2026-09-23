"""Alert lifecycle management service."""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.alert import Alert

def get_alerts(db: Session, status: Optional[str] = None) -> List[Alert]:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.risk_score.desc(), Alert.created_at.desc()).all()

def update_alert_status(db: Session, alert_id: str, new_status: str) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = new_status
        db.commit()
        db.refresh(alert)
    return alert
