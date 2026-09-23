"""Anti-gaming safeguards to detect spamming and coordinated falsification.

Uses timezone-aware UTC datetime normalization to prevent offset-naive/aware comparison errors.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def to_utc(dt: Any) -> datetime:
    """Normalize any datetime or ISO string to UTC-aware datetime."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime.now(timezone.utc)

def check_anti_gaming(
    user_incidents: List[Dict[str, Any]],
    max_reports_per_hour: int = 5
) -> Dict[str, Any]:
    """
    Detect suspicious velocity from a single reporter or identical coordinates bursts.
    All timestamp comparisons are guaranteed timezone-aware UTC.
    """
    if not user_incidents:
        return {"flagged": False, "reason": None}

    now_utc = datetime.now(timezone.utc)
    one_hour_ago = now_utc - timedelta(hours=1)
    
    recent_reports = [
        inc for inc in user_incidents 
        if inc.get("created_at") and to_utc(inc["created_at"]) >= one_hour_ago
    ]

    if len(recent_reports) > max_reports_per_hour:
        return {
            "flagged": True,
            "reason": f"High submission velocity ({len(recent_reports)} reports within 1 hour window)",
            "action": "THROTTLE_AND_AUDIT"
        }

    # Check identical coordinate bursts
    coords = [
        (round(float(inc["latitude"]), 5), round(float(inc["longitude"]), 5)) 
        for inc in user_incidents if "latitude" in inc and "longitude" in inc
    ]
    if len(coords) >= 4 and len(set(coords)) == 1:
        return {
            "flagged": True,
            "reason": "Repeated identical coordinates in rapid succession",
            "action": "MANUAL_VERIFICATION_REQUIRED"
        }

    return {"flagged": False, "reason": None}
