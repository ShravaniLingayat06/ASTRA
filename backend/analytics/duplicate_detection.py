"""Spatiotemporal duplicate report identification with confidence scoring.

Calculates multi-dimensional duplicate probability rather than naive binary matching,
preserving original records while flagging corroboration confidence.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from backend.analytics.spatial_clustering import haversine_distance_km

def to_utc(dt: Any) -> datetime:
    if isinstance(dt, datetime):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def jaccard_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0
    s1 = set(text1.lower().replace(",", "").replace(".", "").split())
    s2 = set(text2.lower().replace(",", "").replace(".", "").split())
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def detect_duplicates(
    incidents: List[Dict[str, Any]],
    distance_threshold_km: float = 0.05,  # 50 meters
    time_window_minutes: int = 30
) -> List[Dict[str, Any]]:
    """
    Detect pairs of incidents that likely represent the same physical event.
    Returns list of candidate duplicate pairings with computed confidence score (0-100%).
    """
    duplicates = []
    n = len(incidents)
    
    for i in range(n):
        for j in range(i + 1, n):
            inc1 = incidents[i]
            inc2 = incidents[j]

            # 1. Geographic proximity score
            dist_km = haversine_distance_km(
                inc1["latitude"], inc1["longitude"],
                inc2["latitude"], inc2["longitude"]
            )
            if dist_km > distance_threshold_km * 2.0:
                continue

            dist_score = max(0.0, 1.0 - (dist_km / max(distance_threshold_km, 0.01)))

            # 2. Temporal proximity score
            t1 = to_utc(inc1["timestamp"])
            t2 = to_utc(inc2["timestamp"])
            time_diff_min = abs((t1 - t2).total_seconds()) / 60.0
            if time_diff_min > time_window_minutes * 2.0:
                continue

            time_score = max(0.0, 1.0 - (time_diff_min / max(time_window_minutes, 1.0)))

            # 3. Incident taxonomy score
            type1 = str(inc1.get("incident_type", "")).lower()
            type2 = str(inc2.get("incident_type", "")).lower()
            type_score = 1.0 if type1 == type2 else (0.6 if type1 in type2 or type2 in type1 else 0.2)

            # 4. Description content similarity
            desc1 = str(inc1.get("description") or "")
            desc2 = str(inc2.get("description") or "")
            desc_score = jaccard_similarity(desc1, desc2)

            # Composite confidence score
            confidence = (dist_score * 0.40) + (time_score * 0.35) + (type_score * 0.15) + (desc_score * 0.10)
            confidence_pct = round(confidence * 100.0, 1)

            if confidence_pct >= 60.0:
                duplicates.append({
                    "incident_id_1": inc1["id"],
                    "incident_id_2": inc2["id"],
                    "confidence": confidence_pct,
                    "distance_meters": round(dist_km * 1000.0, 1),
                    "time_diff_minutes": round(time_diff_min, 1),
                    "reason": f"Likely co-witness report: {round(dist_km*1000, 0)}m apart, {round(time_diff_min, 0)} min delta."
                })
                        
    return duplicates
