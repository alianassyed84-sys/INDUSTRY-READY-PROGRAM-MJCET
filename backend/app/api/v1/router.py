from fastapi import APIRouter, Depends

from app.api.v1 import (
    analysis,
    harvester,
    health,
    language_detection,
    sentiment,
    topics,
)
from app.core.auth import get_current_user
from app.core.rate_limit import rate_limit_analysis

api_router = APIRouter()

# Public, unauthenticated, rate-limit exempt endpoints
api_router.include_router(health.router)

# Authenticated NLP analysis endpoints with rate limiting
analysis_deps = [Depends(get_current_user), Depends(rate_limit_analysis)]

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"],
    dependencies=analysis_deps,
)
api_router.include_router(
    language_detection.router,
    prefix="/analysis",
    tags=["analysis"],
    dependencies=analysis_deps,
)
api_router.include_router(
    topics.router,
    prefix="/analysis",
    tags=["analysis"],
    dependencies=analysis_deps,
)
api_router.include_router(
    sentiment.router,
    prefix="/analysis",
    tags=["analysis"],
    dependencies=analysis_deps,
)

# Harvester endpoints (authenticated / administrative dependencies defined per-route)
api_router.include_router(harvester.router, prefix="/harvester", tags=["harvester"])
