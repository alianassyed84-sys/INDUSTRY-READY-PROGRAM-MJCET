from fastapi import APIRouter

from app.api.v1 import (
    analysis,
    harvester,
    health,
    language_detection,
    sentiment,
    topics,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(
    language_detection.router, prefix="/analysis", tags=["analysis"]
)
api_router.include_router(topics.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(sentiment.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(harvester.router, prefix="/harvester", tags=["harvester"])
