from fastapi import APIRouter

from app.api.v1 import farms, health, jobs, observations, paddocks, recommendations, weather

api_router = APIRouter()
api_router.include_router(health.router, tags=['health'])
api_router.include_router(farms.router, prefix='/farms', tags=['farms'])
api_router.include_router(paddocks.router, tags=['paddocks'])
api_router.include_router(observations.router, tags=['observations'])
api_router.include_router(weather.router, tags=['weather'])
api_router.include_router(recommendations.router, tags=['recommendations'])
api_router.include_router(jobs.router, tags=['jobs'])
