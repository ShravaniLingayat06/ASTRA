from fastapi import APIRouter
from .auth import router as auth_router
from .incidents import router as incidents_router
from .patterns import router as patterns_router
from .alerts import router as alerts_router
from .reviews import router as reviews_router
from .dashboard import router as dashboard_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(incidents_router)
api_router.include_router(patterns_router)
api_router.include_router(alerts_router)
api_router.include_router(reviews_router)
api_router.include_router(dashboard_router)
