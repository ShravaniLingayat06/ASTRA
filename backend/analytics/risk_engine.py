"""ASTRA Core Risk Engine: Connects the dots instead of counting incidents."""
from datetime import datetime, timezone
from typing import List, Dict, Any
from backend.config import settings
from backend.analytics.spatial_clustering import (
    perform_spatial_clustering,
    compute_cluster_metrics
)
from backend.analytics.time_patterns import analyze_time_patterns
from backend.analytics.frequency import analyze_frequency
from backend.analytics.trend_detection import analyze_trend
from backend.analytics.reporter_diversity import analyze_reporter_diversity
from backend.analytics.behaviour_similarity import analyze_behaviour_similarity

def calculate_cluster_risk(incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesize multi-signal analysis for a group of clustered incidents into an
    explainable safety pattern and risk assessment.
    
    Combines all 6 pillars from PPT Slide 6:
    1. Spatial Clustering
    2. Time Patterns
    3. Frequency / Surge
    4. Trend & Escalation
    5. Reporter Diversity (human witnesses + system signals)
    6. Behaviour / MO Similarity
    """
    if not incidents:
        return {
            "risk_score": 0.0,
            "pattern_level": "NORMAL",
            "explanation": "No incidents provided.",
            "evidence": {}
        }

    # Extract raw telemetry signals
    coords = [(inc["latitude"], inc["longitude"]) for inc in incidents]
    timestamps = [inc["timestamp"] for inc in incidents]
    severities = [inc.get("severity", 3) for inc in incidents]
    reporter_ids = [inc.get("reporter_id") for inc in incidents]
    reporter_types = [inc.get("reporter_type", "citizen") for inc in incidents]
    incident_types = [inc.get("incident_type", "unknown") for inc in incidents]
    descriptions = [inc.get("description", "") for inc in incidents]

    # Execute individual pillar analytics
    spatial_res = compute_cluster_metrics(coords)
    time_res = analyze_time_patterns(timestamps)
    freq_res = analyze_frequency(timestamps)
    trend_res = analyze_trend(timestamps, severities)
    div_res = analyze_reporter_diversity(reporter_ids, reporter_types)
    mo_res = analyze_behaviour_similarity(incident_types, descriptions)

    # 6-Pillar Weighted Composite Risk Score (Sum of weights = 1.0)
    score = (
        spatial_res["spatial_score"] * settings.WEIGHT_SPATIAL +
        time_res["temporal_score"] * settings.WEIGHT_TEMPORAL +
        freq_res["frequency_score"] * settings.WEIGHT_FREQUENCY +
        trend_res["trend_score"] * settings.WEIGHT_TREND +
        div_res["diversity_score"] * settings.WEIGHT_DIVERSITY +
        mo_res["mo_similarity_score"] * settings.WEIGHT_BEHAVIOUR
    )
    risk_score = round(min(100.0, max(0.0, score)), 1)

    # Map to pattern level thresholds
    if risk_score >= settings.THRESHOLD_ESCALATING:
        pattern_level = "ESCALATING"
    elif risk_score >= settings.THRESHOLD_CONCERNING:
        pattern_level = "CONCERNING"
    elif risk_score >= settings.THRESHOLD_EMERGING:
        pattern_level = "EMERGING"
    else:
        pattern_level = "NORMAL"

    sorted_ts = sorted(timestamps)
    first_seen = sorted_ts[0]
    last_seen = sorted_ts[-1]

    # Rigorous, explainable narrative: distinguishes human witnesses from automated sensors
    mo_traits_str = f" [Traits: {', '.join(mo_res['detected_mo_traits'])}]" if mo_res['detected_mo_traits'] else ""
    threat_family = mo_res.get('primary_threat_family', mo_res['primary_threat_type'].replace('_', ' ').title())
    explanation_parts = [
        f"{pattern_level} pattern identified across {len(incidents)} incidents within a {spatial_res['radius_meters']}m radius.",
        f"Modus Operandi: {threat_family} — {mo_res['mo_similarity_score']}% MO consistency{mo_traits_str}.",
        f"Temporal concentration: {time_res['time_window']} (Night ratio: {int(time_res['night_ratio']*100)}%).",
        f"Human corroboration: {div_res['unique_human_reporters']} independent witness(es) ({div_res['human_corroboration']}). "
        f"Supporting signals: {div_res['unique_system_sources']} automated sensor/CCTV source(s).",
        f"Trend: {trend_res['trend_direction']} ({trend_res['acceleration']}) — incident velocity {freq_res['incident_rate_per_day']} /day."
    ]
    explanation = " ".join(explanation_parts)

    evidence = {
        "spatial": spatial_res,
        "temporal": time_res,
        "frequency": freq_res,
        "trend": trend_res,
        "diversity": div_res,
        "behaviour": mo_res,
        "weights": {
            "spatial": settings.WEIGHT_SPATIAL,
            "temporal": settings.WEIGHT_TEMPORAL,
            "frequency": settings.WEIGHT_FREQUENCY,
            "trend": settings.WEIGHT_TREND,
            "diversity": settings.WEIGHT_DIVERSITY,
            "behaviour": settings.WEIGHT_BEHAVIOUR
        }
    }

    return {
        "risk_score": risk_score,
        "pattern_level": pattern_level,
        "explanation": explanation,
        "evidence": evidence,
        "centroid": spatial_res["centroid"],
        "radius_meters": spatial_res["radius_meters"],
        "time_window": time_res["time_window"],
        "reporter_diversity": div_res["unique_human_reporters"],
        "trend_score": trend_res["trend_score"],
        "behaviour_score": mo_res["mo_similarity_score"],
        "first_seen": first_seen,
        "last_seen": last_seen,
        "incident_types": list(set(incident_types)),
        "incident_ids": [inc["id"] for inc in incidents if "id" in inc]
    }
