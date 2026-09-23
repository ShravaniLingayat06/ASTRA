"""ASTRA - Context-Aware Safety Intelligence Platform: Main FastAPI Application."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database.connection import engine, Base, SessionLocal
from backend.api import api_router
from data.synthetic_generator import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created
    print("Initializing ASTRA Database & Intelligence Engine...")
    Base.metadata.create_all(bind=engine)
    
    # Configurable demo data seeding (toggled via SEED_DEMO_DATA in .env)
    if settings.SEED_DEMO_DATA:
        db = SessionLocal()
        try:
            seed_database(db)
        except Exception as e:
            print(f"Startup seeding notice: {e}")
        finally:
            db.close()
    else:
        print("SEED_DEMO_DATA is False: Production mode active (skipping synthetic seeding).")
        
    print("ASTRA Safety Intelligence Platform is online!")
    yield
    print("Shutting down ASTRA Platform...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Connect the dots instead of counting incidents: Context-aware multi-signal safety intelligence.",
    lifespan=lifespan
)

# Explicit CORS configuration (Restricted to configured domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount frontend interfaces (legacy fallback & modern React shadcn app)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
react_dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend-react", "dist"))

if os.path.exists(react_dist_dir):
    assets_dir = os.path.join(react_dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    app.mount("/app", StaticFiles(directory=react_dist_dir, html=True), name="react-app")

if os.path.exists(frontend_dir):
    app.mount("/legacy", StaticFiles(directory=frontend_dir, html=True), name="legacy")
    app.mount("/legacy/citizen", StaticFiles(directory=os.path.join(frontend_dir, "citizen")), name="legacy-citizen")
    app.mount("/legacy/security", StaticFiles(directory=os.path.join(frontend_dir, "security")), name="legacy-security")
    app.mount("/legacy/authority", StaticFiles(directory=os.path.join(frontend_dir, "authority")), name="legacy-authority")

@app.get("/favicon.svg")
def serve_favicon():
    fav_path = os.path.join(react_dist_dir, "favicon.svg")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/icons.svg")
def serve_icons():
    icons_path = os.path.join(react_dist_dir, "icons.svg")
    if os.path.exists(icons_path):
        return FileResponse(icons_path)
    return {}

# Support legacy HTML file routes mentioned in documentation
@app.get("/citizen/report.html")
def serve_legacy_citizen():
    return FileResponse(os.path.join(frontend_dir, "citizen", "report.html"))

@app.get("/security/monitor.html")
def serve_legacy_security():
    return FileResponse(os.path.join(frontend_dir, "security", "monitor.html"))

@app.get("/authority/dashboard.html")
def serve_legacy_authority():
    return FileResponse(os.path.join(frontend_dir, "authority", "dashboard.html"))

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    # If React dist exists, serve its index.html for SPA routing
    if os.path.exists(react_dist_dir):
        index_file = os.path.join(react_dist_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    portal_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(portal_path):
        return FileResponse(portal_path)
    return {"status": "ASTRA Intelligence Engine Active"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ASTRA Safety Intelligence Platform",
        "version": settings.VERSION,
        "database": "SQLite (Dev) / PostgreSQL compatible"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
