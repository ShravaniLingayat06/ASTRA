"""Reporter diversity and independent corroboration analysis.

Differentiates:
1. Unique human witnesses (citizens, students, security patrol officers)
2. Distinct signal sources (citizen app, patrol log, CCTV AI detector, sensor telemetry)
"""
from typing import List, Dict, Any

AUTOMATED_SOURCES = {"camera_cv", "cctv_ai", "sensor", "automated_geofence"}

def analyze_reporter_diversity(reporter_ids: List[str], reporter_types: List[str]) -> Dict[str, Any]:
    """
    Evaluate credibility via multi-source independent corroboration.
    Distinguishes independent human witnesses from supporting automated sensor/camera signals.
    """
    valid_ids = [r for r in reporter_ids if r]
    total_reports = len(reporter_types)

    if total_reports == 0:
        return {
            "unique_human_reporters": 0,
            "unique_system_sources": 0,
            "unique_source_channels": 0,
            "diversity_score": 0.0,
            "is_single_source": True,
            "human_corroboration": "None",
            "types_breakdown": []
        }

    # Separate human reporters from automated systems
    human_reporter_ids = []
    system_signals = []
    for rep_id, r_type in zip(reporter_ids, reporter_types):
        if r_type in AUTOMATED_SOURCES or (rep_id and "camera" in rep_id.lower()):
            system_signals.append(r_type)
        else:
            human_reporter_ids.append(rep_id or "anonymous_citizen")

    unique_human_count = len(set(human_reporter_ids))
    unique_system_count = len(set(system_signals))
    unique_channel_count = len(set(reporter_types))

    # Single-source flag applies if all reports came from one person with no other corroboration
    is_single_source = (unique_human_count == 1 and unique_system_count == 0 and total_reports >= 2)

    # Diversity score calculation:
    # 1. Independent human reporters (primary weight)
    # 2. Multi-channel corroboration (e.g. citizen report + CCTV AI flag + security patrol)
    base_score = 25.0
    if is_single_source:
        base_score = 20.0
    else:
        # Human corroboration: 1 human = +10, 2 humans = +25, 3+ humans = +40
        base_score += min(45.0, unique_human_count * 15.0)
        # Supporting system telemetry: +15 if corroborated by automated CCTV/sensor
        if unique_system_count > 0:
            base_score += min(25.0, unique_system_count * 15.0)
        # Multiple distinct channel types
        base_score += min(15.0, (unique_channel_count - 1) * 8.0)

    diversity_score = min(100.0, max(15.0, base_score))

    human_corroboration_level = "Weak (1 Reporter)"
    if unique_human_count >= 4:
        human_corroboration_level = "Strong (4+ Independent Witnesses)"
    elif unique_human_count >= 2:
        human_corroboration_level = "Moderate (2-3 Independent Witnesses)"

    return {
        "unique_human_reporters": unique_human_count,
        "unique_system_sources": unique_system_count,
        "unique_source_channels": unique_channel_count,
        "diversity_score": round(diversity_score, 2),
        "is_single_source": is_single_source,
        "human_corroboration": human_corroboration_level,
        "types_breakdown": list(set(reporter_types))
    }
