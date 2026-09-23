"""Human review API routes for authority decisions."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.review import ReviewCreate, ReviewOut
from backend.services.review_service import create_review, get_reviews_for_pattern
from backend.security.rbac import require_authority
from backend.models.user import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewOut)
def submit_review(
    rev_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authority)
):
    """Authority human review submission (verifies, dismisses, or takes action on pattern)."""
    return create_review(db, rev_in, reviewer_id=current_user.id)

@router.get("/pattern/{pattern_id}", response_model=List[ReviewOut])
def list_pattern_reviews(pattern_id: str, db: Session = Depends(get_db)):
    return get_reviews_for_pattern(db, pattern_id)
