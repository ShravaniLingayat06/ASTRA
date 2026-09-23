"""Frequency analysis and surge velocity calculation."""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def analyze_frequency(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Calculate incident occurrence rate, recurrence, and frequency score (0-100).
    """
    count = len(timestamps)
    if count <= 1:
        return {
            "incident_rate_per_day": 0.0,
            "frequency_score": 15.0 if count == 1 else 0.0,
            "surge_factor": 1.0
        }

    sorted_ts = sorted(timestamps)
    earliest = sorted_ts[0]
    latest = sorted_ts[-1]
    span_days = max((latest - earliest).total_seconds() / 86400.0, 0.04)  # min ~1 hour
    
    rate_per_day = count / span_days
    
    # Check recent surge: incidents in the last 48 hours vs previous baseline
    now = latest
    last_48h_cutoff = now - timedelta(hours=48)
    recent_count = sum(1 for ts in sorted_ts if ts >= last_48h_cutoff)
    older_count = count - recent_count
    
    surge_factor = 1.0
    if older_count > 0:
        surge_factor = (recent_count / 2.0) / max(older_count / max(span_days, 1.0), 0.5)
    elif recent_count >= 3:
        surge_factor = 2.5

    # Frequency score calculation:
    # 2 incidents: ~30-40, 5 incidents: ~60-70, 10+ incidents: ~85-100
    base_score = min(75.0, count * 10.0)
    surge_bonus = min(25.0, (surge_factor - 1.0) * 15.0) if surge_factor > 1.0 else 0.0
    frequency_score = min(100.0, max(10.0, base_score + surge_bonus))

    return {
        "incident_rate_per_day": round(rate_per_day, 2),
        "frequency_score": round(frequency_score, 2),
        "surge_factor": round(surge_factor, 2),
        "recent_48h_count": recent_count
    }
