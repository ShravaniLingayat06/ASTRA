"""Publishes automated computer vision anomaly signals to ASTRA backend."""
import requests
from datetime import datetime, timezone

class SignalPublisher:
    def __init__(self, backend_url: str = "http://127.0.0.1:8000"):
        self.backend_url = backend_url

    def publish_cv_incident(
        self,
        incident_type: str,
        description: str,
        latitude: float,
        longitude: float,
        severity: int = 3
    ):
        """Send an automated CCTV / CV signal to ASTRA incident ingestion endpoint."""
        url = f"{self.backend_url}/api/incidents/"
        payload = {
            "incident_type": incident_type,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "reporter_type": "camera_cv",
            "source": "cctv_ai",
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            resp = requests.post(url, json=payload, timeout=3.0)
            return resp.status_code in (200, 201)
        except Exception as e:
            print(f"Warning: Failed to publish CV signal to ASTRA backend: {e}")
            return False
