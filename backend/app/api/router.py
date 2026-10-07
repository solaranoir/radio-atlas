from fastapi import APIRouter

from app.api.routes.observations import router as observations_router
from app.api.routes.replay import router as replay_router
from app.api.routes.solar_conditions import router as solar_conditions_router
from app.api.routes.stations import router as stations_router
from app.api.routes.statistics import router as statistics_router
from app.api.routes.timeline import router as timeline_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(observations_router)
api_router.include_router(replay_router)
api_router.include_router(solar_conditions_router)
api_router.include_router(stations_router)
api_router.include_router(statistics_router)
api_router.include_router(timeline_router)
