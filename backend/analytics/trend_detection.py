"""Trend detection and escalation velocity analysis."""
from datetime import datetime, timedelta
from typing import List, Dict, Any

def analyze_trend(timestamps: List[datetime], severities: List[int]) -> Dict[str, Any]:
    """
    Detect whether incidents are escalating in frequency or severity.
    Computes trend_score (0-100) and escalation direction.
    """
    if len(timestamps) < 2:
        return {
            "trend_direction": "STABLE",
            "trend_score": 20.0,
            "severity_slope": 0.0,
            "acceleration": "FLAT"
        }

    # Sort pairs by timestamp
    pairs = sorted(zip(timestamps, severities), key=lambda x: x[0])
    ts_sorted = [p[0] for p in pairs]
    sev_sorted = [p[1] for p in pairs]

    # Split into first half and second half
    half = len(pairs) // 2
    first_half_sevs = sev_sorted[:half]
    second_half_sevs = sev_sorted[half:]

    avg_sev_early = sum(first_half_sevs) / max(len(first_half_sevs), 1)
    avg_sev_recent = sum(second_half_sevs) / max(len(second_half_sevs), 1)
    severity_diff = avg_sev_recent - avg_sev_early

    # Check temporal acceleration: are gaps between incidents shrinking?
    intervals = []
    for i in range(1, len(ts_sorted)):
        diff_hours = (ts_sorted[i] - ts_sorted[i-1]).total_seconds() / 3600.0
        intervals.append(diff_hours)

    first_intervals = intervals[:max(len(intervals)//2, 1)]
    second_intervals = intervals[max(len(intervals)//2, 1):]

    early_interval_avg = sum(first_intervals) / max(len(first_intervals), 1)
    recent_interval_avg = sum(second_intervals) / max(len(second_intervals), 1) if second_intervals else early_interval_avg

    interval_shrink_ratio = early_interval_avg / max(recent_interval_avg, 0.1)

    trend_score = 40.0
    if severity_diff > 0.5:
        trend_score += 25.0
    elif severity_diff < -0.5:
        trend_score -= 15.0

    if interval_shrink_ratio > 1.5:  # incidents occurring much closer together
        trend_score += 30.0
        acceleration = "ACCELERATING"
        trend_direction = "ESCALATING"
    elif interval_shrink_ratio < 0.7:
        trend_score -= 10.0
        acceleration = "DECELERATING"
        trend_direction = "SUBSIDING"
    else:
        acceleration = "STEADY"
        trend_direction = "ESCALATING" if severity_diff > 0.5 else "STABLE"

    trend_score = min(100.0, max(0.0, trend_score))

    return {
        "trend_direction": trend_direction,
        "trend_score": round(trend_score, 2),
        "severity_slope": round(float(severity_diff), 2),
        "acceleration": acceleration,
        "avg_severity_recent": round(float(avg_sev_recent), 2)
    }
