"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import close_database
from app.core.errors import register_exception_handlers
from app.core.logging import RequestIdMiddleware, configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.database_url:
        try:
            from app.core.database import Base, get_engine, get_sessionmaker
            from app.services.harvester.catalog_seeder import seed_catalog

            engine = get_engine(settings.database_url, settings=settings)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            sessionmaker = get_sessionmaker(settings.database_url, settings=settings)
            async with sessionmaker() as session:
                await seed_catalog(session)
        except Exception as exc:
            logger.warning("Startup DB initialization/seeding skipped: %s", exc)
    yield
    await close_database()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an application instance that does not require a live database."""
    resolved = settings or get_settings()
    if settings is None and not resolved.database_url:
        # ponytail: fallback to local SQLite for rapid zero-config dev; upgrade to mandatory PostgreSQL check when ENVIRONMENT == "production"
        resolved.database_url = "sqlite+aiosqlite:///reviewpulse.db"

    configure_logging(resolved)

    application = FastAPI(
        title="ReviewPulse API",
        version="0.1.0",
        lifespan=lifespan,
    )

    cors_allowed = list(resolved.cors_origins)
    for origin in (
        "https://reviewpulse-peach.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ):
        if origin not in cors_allowed:
            cors_allowed.append(origin)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allowed,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    application.add_middleware(RequestIdMiddleware)
    register_exception_handlers(application)
    @application.get("/", include_in_schema=False)
    def root_endpoint() -> dict[str, str]:
        return {
            "service": resolved.app_name,
            "status": "ok",
            "docs": "/docs",
            "health": f"{resolved.api_v1_prefix}/health",
        }

    application.include_router(api_router, prefix=resolved.api_v1_prefix)
    return application


app = create_app()

