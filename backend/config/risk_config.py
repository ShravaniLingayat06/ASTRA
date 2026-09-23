"""ASTRA Risk and Intelligence Engine Configuration."""
import os
from typing import List

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ASTRA - Safety Intelligence Platform")
    VERSION: str = os.getenv("VERSION", "1.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "astra-secret-key-change-in-production-cx1001")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
    ALGORITHM: str = "HS256"
    
    # CORS: Explicitly configured allowed origins (no wildcard with credentials)
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5000,http://127.0.0.1:5000"
        ).split(",") if origin.strip()
    ]

    # Database: Development defaults to SQLite; Production configures PostgreSQL + PostGIS
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./astra.db")
    
    # Startup Seeding: Toggleable for demo vs real production deployment
    SEED_DEMO_DATA: bool = os.getenv("SEED_DEMO_DATA", "true").lower() in ("true", "1", "yes")

    # 6-Pillar Risk Engine Weights (Sum to exactly 1.0)
    # Reflects PPT Slide 6: Location + Time + Frequency + Diversity + Trend + Behaviour
    WEIGHT_SPATIAL: float = float(os.getenv("WEIGHT_SPATIAL", "0.20"))
    WEIGHT_TEMPORAL: float = float(os.getenv("WEIGHT_TEMPORAL", "0.15"))
    WEIGHT_FREQUENCY: float = float(os.getenv("WEIGHT_FREQUENCY", "0.15"))
    WEIGHT_TREND: float = float(os.getenv("WEIGHT_TREND", "0.15"))
    WEIGHT_DIVERSITY: float = float(os.getenv("WEIGHT_DIVERSITY", "0.20"))
    WEIGHT_BEHAVIOUR: float = float(os.getenv("WEIGHT_BEHAVIOUR", "0.15"))

    # Clustering Parameters
    DBSCAN_EPS_KM: float = float(os.getenv("DBSCAN_EPS_KM", "0.5"))  # 500 meters
    DBSCAN_MIN_SAMPLES: int = int(os.getenv("DBSCAN_MIN_SAMPLES", "2"))
    
    # Spatio-temporal Duplicate Confidence Parameters
    DUP_DISTANCE_THRESHOLD_KM: float = float(os.getenv("DUP_DISTANCE_THRESHOLD_KM", "0.05")) # 50 meters
    DUP_TIME_WINDOW_MINUTES: int = int(os.getenv("DUP_TIME_WINDOW_MINUTES", "30"))
    
    # Anti-gaming Thresholds
    MAX_REPORTS_PER_USER_PER_HOUR: int = int(os.getenv("MAX_REPORTS_PER_USER_PER_HOUR", "5"))
    
    # Risk Level Categorization Thresholds
    THRESHOLD_EMERGING: float = float(os.getenv("THRESHOLD_EMERGING", "25.0"))
    THRESHOLD_CONCERNING: float = float(os.getenv("THRESHOLD_CONCERNING", "50.0"))
    THRESHOLD_ESCALATING: float = float(os.getenv("THRESHOLD_ESCALATING", "75.0"))

settings = Settings()
