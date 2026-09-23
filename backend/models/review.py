import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class PatternReview(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    pattern_id = Column(String(36), ForeignKey("patterns.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    decision = Column(String(50), nullable=False)  # CONFIRMED_THREAT, FALSE_POSITIVE, PATROL_DISPATCHED, MONITORING
    notes = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pattern = relationship("SafetyPattern", foreign_keys=[pattern_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
