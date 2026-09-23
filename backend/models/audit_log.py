import uuid
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from backend.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class AuditLog(Base):
    """
    Append-only, tamper-evident audit log implementing SHA-256 hash chaining.
    Each record seals the hash of the preceding entry.
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(36), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    previous_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=True)

    def compute_hash(self, prev_hash: str = "GENESIS") -> str:
        payload = f"{prev_hash}:{self.user_id}:{self.action}:{self.resource_id}:{self.timestamp.isoformat() if self.timestamp else ''}:{json.dumps(self.metadata_json or {}, sort_keys=True)}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
