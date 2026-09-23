"""Temporal pattern analysis and time-window concentration."""
from datetime import datetime
from typing import List, Dict, Any

def analyze_time_patterns(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Analyze timestamps to detect peak time windows, night-time concentration,
    and temporal concentration score (0-100).
    """
    if not timestamps:
        return {
            "time_window": "Insufficient Data",
            "night_ratio": 0.0,
            "temporal_score": 0.0,
            "span_hours": 0.0
        }

    hours = [ts.hour for ts in timestamps]
    
    # Categorize into windows: Night (21-05), Morning (05-12), Afternoon (12-17), Evening (17-21)
    night_count = sum(1 for h in hours if h >= 21 or h < 5)
    evening_count = sum(1 for h in hours if 17 <= h < 21)
    afternoon_count = sum(1 for h in hours if 12 <= h < 17)
    morning_count = sum(1 for h in hours if 5 <= h < 12)
    
    total = len(timestamps)
    windows = {
        "Night (21:00 - 05:00)": night_count,
        "Evening (17:00 - 21:00)": evening_count,
        "Afternoon (12:00 - 17:00)": afternoon_count,
        "Morning (05:00 - 12:00)": morning_count
    }
    dominant_window = max(windows, key=windows.get)
    night_ratio = night_count / total

    # Time span
    sorted_ts = sorted(timestamps)
    span_hours = (sorted_ts[-1] - sorted_ts[0]).total_seconds() / 3600.0

    # Temporal score:
    # High score when:
    # 1. Concentrated in high-risk hours (Night / Late Evening)
    # 2. Clustered within a tight recurring daily window
    base_score = 30.0
    if "Night" in dominant_window:
        base_score += 35.0 * (windows[dominant_window] / total)
    elif "Evening" in dominant_window:
        base_score += 25.0 * (windows[dominant_window] / total)
    else:
        base_score += 15.0 * (windows[dominant_window] / total)

    # If recurrent across multiple days in same window, increase score
    unique_days = len(set(ts.strftime('%Y-%m-%d') for ts in timestamps))
    if unique_days >= 2 and (windows[dominant_window] / total) >= 0.5:
        base_score += 20.0

    temporal_score = min(100.0, max(0.0, base_score))

    return {
        "time_window": dominant_window,
        "night_ratio": round(night_ratio, 2),
        "temporal_score": round(temporal_score, 2),
        "span_hours": round(span_hours, 1),
        "distribution": windows
    }
