import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reporter_type = Column(String(50), nullable=False, default="citizen")  # citizen, security, camera_cv, authority
    source = Column(String(50), nullable=False, default="manual")  # manual, cctv_ai, app, sensor
    severity = Column(Integer, nullable=False, default=3)  # 1 to 5
    status = Column(String(50), nullable=False, default="active")
    duplicate_candidate = Column(Boolean, default=False)
    cluster_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reporter = relationship("User", foreign_keys=[reporter_id])
