"""Pattern detection service: clusters active incidents and calculates risk profiles."""
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from backend.models.incident import Incident
from backend.models.pattern import SafetyPattern
from backend.models.alert import Alert
from backend.analytics.spatial_clustering import perform_spatial_clustering
from backend.analytics.risk_engine import calculate_cluster_risk
from backend.config import settings

def refresh_safety_patterns(db: Session) -> List[SafetyPattern]:
    """
    Run spatial-temporal clustering across all active incidents,
    derive risk scores, update/create patterns, and generate alerts.
    """
    active_incidents = db.query(Incident).filter(Incident.status == "active").all()
    if not active_incidents:
        return []

    coords = [(inc.latitude, inc.longitude) for inc in active_incidents]
    labels = perform_spatial_clustering(
        coords,
        eps_km=settings.DBSCAN_EPS_KM,
        min_samples=settings.DBSCAN_MIN_SAMPLES
    )

    # Group incidents by cluster label
    clusters = {}
    for idx, label in enumerate(labels):
        active_incidents[idx].cluster_id = label
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(active_incidents[idx])
    
    db.commit()

    generated_patterns = []
    
    # Process each cluster (excluding noise label -1 unless it has multiple points)
    for label, cluster_incs in clusters.items():
        if label == -1 and len(cluster_incs) < 3:
            continue

        inc_dicts = [
            {
                "id": inc.id,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "timestamp": inc.timestamp,
                "severity": inc.severity,
                "reporter_id": inc.reporter_id,
                "reporter_type": inc.reporter_type,
                "incident_type": inc.incident_type,
                "description": inc.description
            }
            for inc in cluster_incs
        ]

        analysis = calculate_cluster_risk(inc_dicts)

        # Check if an existing pattern matches this cluster
        pattern = db.query(SafetyPattern).filter(
            SafetyPattern.cluster_id == label,
            SafetyPattern.status != "RESOLVED"
        ).first()

        if not pattern:
            pattern = SafetyPattern(
                cluster_id=label,
                title=f"Pattern #{abs(label)}: {analysis['evidence']['behaviour']['primary_threat_type'].title()} Cluster"
            )
            db.add(pattern)

        pattern.incident_count = len(cluster_incs)
        pattern.incident_types = analysis["incident_types"]
        pattern.incident_ids = analysis["incident_ids"]
        pattern.first_seen = analysis["first_seen"]
        pattern.last_seen = analysis["last_seen"]
        pattern.latitude = analysis["centroid"][0]
        pattern.longitude = analysis["centroid"][1]
        pattern.radius_meters = analysis["radius_meters"]
        pattern.time_window = analysis["time_window"]
        pattern.reporter_diversity = analysis["reporter_diversity"]
        pattern.trend_score = analysis["trend_score"]
        pattern.risk_score = analysis["risk_score"]
        pattern.pattern_level = analysis["pattern_level"]
        pattern.explanation = analysis["explanation"]
        pattern.evidence = analysis["evidence"]
        
        db.commit()
        db.refresh(pattern)
        generated_patterns.append(pattern)

        # Create or update alert if risk warrants attention
        if pattern.pattern_level in ("CONCERNING", "ESCALATING"):
            existing_alert = db.query(Alert).filter(
                Alert.pattern_id == pattern.id,
                Alert.status == "ACTIVE"
            ).first()

            alert_level = "CRITICAL" if pattern.pattern_level == "ESCALATING" else "HIGH"
            rec_action = (
                "Deploy proactive patrol unit during peak hours; audit street lighting; issue citizen safety advisory."
                if pattern.pattern_level == "ESCALATING" else
                "Increase patrol frequency and verify CCTV feeds covering this coordinate radius."
            )

            if not existing_alert:
                new_alert = Alert(
                    pattern_id=pattern.id,
                    alert_level=alert_level,
                    risk_score=pattern.risk_score,
                    headline=f"⚠️ {pattern.pattern_level} Safety Pattern Detected: {pattern.title}",
                    explanation=pattern.explanation,
                    recommended_action=rec_action,
                    evidence=pattern.evidence,
                    status="ACTIVE"
                )
                db.add(new_alert)
                db.commit()
            else:
                existing_alert.risk_score = pattern.risk_score
                existing_alert.alert_level = alert_level
                existing_alert.explanation = pattern.explanation
                db.commit()

    return generated_patterns

def get_patterns(db: Session) -> List[SafetyPattern]:
    return db.query(SafetyPattern).order_by(SafetyPattern.risk_score.desc()).all()
