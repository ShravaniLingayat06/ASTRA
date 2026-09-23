"""Human-in-the-loop review workflow service with hash-chained audit logging."""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.review import PatternReview
from backend.models.pattern import SafetyPattern
from backend.models.audit_log import AuditLog
from backend.schemas.review import ReviewCreate

def create_review(db: Session, rev_in: ReviewCreate, reviewer_id: Optional[str] = None) -> PatternReview:
    review = PatternReview(
        pattern_id=rev_in.pattern_id,
        reviewer_id=reviewer_id,
        decision=rev_in.decision,
        notes=rev_in.notes,
        action_taken=rev_in.action_taken
    )
    db.add(review)

    # Update pattern status accordingly
    pattern = db.query(SafetyPattern).filter(SafetyPattern.id == rev_in.pattern_id).first()
    if pattern:
        if rev_in.decision == "CONFIRMED_THREAT":
            pattern.status = "VERIFIED"
        elif rev_in.decision == "FALSE_POSITIVE":
            pattern.status = "DISMISSED"
        elif rev_in.decision == "PATROL_DISPATCHED":
            pattern.status = "ACTION_TAKEN"
        elif rev_in.decision == "MONITORING":
            pattern.status = "UNDER_REVIEW"

    # Cryptographic hash-chaining: link to previous audit entry
    last_log = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
    prev_hash = last_log.entry_hash if (last_log and last_log.entry_hash) else "GENESIS_ROOT_HASH_CX1001"

    audit = AuditLog(
        user_id=reviewer_id,
        action=f"REVIEW_SUBMITTED: {rev_in.decision}",
        resource_type="pattern",
        resource_id=rev_in.pattern_id,
        previous_hash=prev_hash,
        metadata_json={"decision": rev_in.decision, "action_taken": rev_in.action_taken}
    )
    audit.entry_hash = audit.compute_hash(prev_hash)
    db.add(audit)

    db.commit()
    db.refresh(review)
    return review

def get_reviews_for_pattern(db: Session, pattern_id: str) -> List[PatternReview]:
    return db.query(PatternReview).filter(PatternReview.pattern_id == pattern_id).all()
