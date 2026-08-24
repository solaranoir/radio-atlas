from fastapi import APIRouter

from app.api.routes.observations import router as observations_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(observations_router)
