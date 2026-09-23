"""Synthetic data generator to seed ground-truth test incidents and users."""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal, Base, engine
from backend.models.user import User
from backend.models.incident import Incident
from backend.security.auth import hash_password
from backend.services.pattern_service import refresh_safety_patterns

def seed_database(db: Session):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # 1. Create Default Seed Users
    users_data = [
        {"name": "System Admin", "email": "admin@astra.safety", "role": "admin", "password": "admin123"},
        {"name": "Inspector Sharma", "email": "authority@astra.safety", "role": "authority", "password": "auth123"},
        {"name": "Patrol Officer Rao", "email": "security@astra.safety", "role": "security", "password": "sec123"},
        {"name": "Pooja Verma", "email": "pooja@example.com", "role": "citizen", "password": "pass123"},
        {"name": "Ananya Sen", "email": "ananya@example.com", "role": "citizen", "password": "pass123"},
        {"name": "Kavita Nair", "email": "kavita@example.com", "role": "citizen", "password": "pass123"}
    ]

    user_map = {}
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                name=u["name"],
                email=u["email"],
                role=u["role"],
                password_hash=hash_password(u["password"])
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            user_map[u["email"]] = user
        else:
            user_map[u["email"]] = existing

    # Check if incidents already seeded
    if db.query(Incident).count() > 0:
        print("Database already contains incidents. Skipping seed.")
        refresh_safety_patterns(db)
        return

    now = datetime.now(timezone.utc)

    # Ground-truth Cluster 1: "The Warning Sign Everyone Walked Past"
    # Brigade Road North Alley - Repeat stalking & harassment after 10 PM
    base_lat_1, base_lon_1 = 12.9716, 77.5946
    cluster_1_incidents = [
        {
            "type": "catcalling_loitering",
            "desc": "Group of men blocking dimly lit corner passing inappropriate remarks",
            "lat": base_lat_1 + 0.00012,
            "lon": base_lon_1 + 0.00008,
            "time": now - timedelta(days=5, hours=2, minutes=15),
            "rep_email": "pooja@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 3
        },
        {
            "type": "stalking",
            "desc": "Individual followed student from bus stop into side street for 200m",
            "lat": base_lat_1 - 0.00009,
            "lon": base_lon_1 + 0.00015,
            "time": now - timedelta(days=3, hours=1, minutes=45),
            "rep_email": "ananya@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 4
        },
        {
            "type": "aggressive_posture",
            "desc": "Camera CV detection: Abnormal loitering and sudden confrontational posture near dark alley",
            "lat": base_lat_1 + 0.00005,
            "lon": base_lon_1 - 0.00007,
            "time": now - timedelta(days=2, hours=3, minutes=10),
            "rep_email": "security@astra.safety",
            "rep_type": "camera_cv",
            "source": "cctv_ai",
            "sev": 4
        },
        {
            "type": "physical_intimidation",
            "desc": "Two individuals aggressively confronted pedestrian demanding phone; fled when bystander shouted",
            "lat": base_lat_1 + 0.00018,
            "lon": base_lon_1 + 0.00004,
            "time": now - timedelta(hours=14, minutes=30),
            "rep_email": "kavita@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 5
        },
        {
            "type": "suspicious_group",
            "desc": "Patrol reported broken streetlight and repeated suspicious loitering at exact corner",
            "lat": base_lat_1 - 0.00010,
            "lon": base_lon_1 - 0.00005,
            "time": now - timedelta(hours=6, minutes=20),
            "rep_email": "security@astra.safety",
            "rep_type": "security",
            "source": "patrol",
            "sev": 4
        }
    ]

    # Ground-truth Cluster 2: Koramangala Transit Hub
    # Pickpocketing and verbal harassment during evening commute
    base_lat_2, base_lon_2 = 12.9352, 77.6245
    cluster_2_incidents = [
        {
            "type": "verbal_harassment",
            "desc": "Verbal abuse near metro entry stairs during peak exit crowd",
            "lat": base_lat_2 + 0.00015,
            "lon": base_lon_2 - 0.00010,
            "time": now - timedelta(days=4, hours=5),
            "rep_email": "pooja@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 2
        },
        {
            "type": "verbal_harassment",
            "desc": "Crowd congestion harassment near auto stand",
            "lat": base_lat_2 - 0.00008,
            "lon": base_lon_2 + 0.00012,
            "time": now - timedelta(days=2, hours=6),
            "rep_email": "ananya@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 3
        },
        {
            "type": "crowd_anomaly",
            "desc": "CV Detection: high male-to-female ratio spike and sudden dispersal",
            "lat": base_lat_2 + 0.00005,
            "lon": base_lon_2 + 0.00002,
            "time": now - timedelta(hours=18),
            "rep_email": "security@astra.safety",
            "rep_type": "camera_cv",
            "source": "cctv_ai",
            "sev": 3
        }
    ]

    # Isolated incidents
    isolated_incidents = [
        {
            "type": "verbal_dispute",
            "desc": "Minor disagreement between commuters near city park, quickly resolved",
            "lat": 12.9815,
            "lon": 77.6401,
            "time": now - timedelta(days=6, hours=8),
            "rep_email": "pooja@example.com",
            "rep_type": "citizen",
            "source": "manual",
            "sev": 1
        }
    ]

    for item in cluster_1_incidents + cluster_2_incidents + isolated_incidents:
        user_obj = user_map.get(item["rep_email"])
        rep_id = user_obj.id if user_obj else None
        inc = Incident(
            incident_type=item["type"],
            description=item["desc"],
            latitude=item["lat"],
            longitude=item["lon"],
            timestamp=item["time"],
            reporter_id=rep_id,
            reporter_type=item["rep_type"],
            source=item["source"],
            severity=item["sev"],
            status="active"
        )
        db.add(inc)

    db.commit()
    print("Seed incidents inserted successfully!")

    # Calculate patterns & alerts
    patterns = refresh_safety_patterns(db)
    print(f"Generated {len(patterns)} safety intelligence patterns during seeding.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
