import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from backend.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class SafetyPattern(Base):
    __tablename__ = "patterns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=True)
    incident_count = Column(Integer, nullable=False, default=0)
    incident_types = Column(JSON, nullable=True)  # List of incident types
    incident_ids = Column(JSON, nullable=True)    # List of associated incident IDs
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_meters = Column(Float, default=150.0)
    time_window = Column(String(100), nullable=True)  # e.g., "Night (22:00-03:00)"
    reporter_diversity = Column(Integer, default=1)
    trend_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    pattern_level = Column(String(50), default="NORMAL")  # NORMAL, EMERGING, CONCERNING, ESCALATING
    status = Column(String(50), default="NEW")            # NEW, UNDER_REVIEW, VERIFIED, DISMISSED, ACTION_TAKEN
    explanation = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
