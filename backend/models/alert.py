import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    pattern_id = Column(String(36), ForeignKey("patterns.id"), nullable=True)
    alert_level = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float, nullable=False)
    headline = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pattern = relationship("SafetyPattern", foreign_keys=[pattern_id])
