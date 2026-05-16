import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth.routes import router as auth_router
from app.config import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.storage.redis_client import RedisClient


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings.app_log_level)
    logger = logging.getLogger("app.lifespan")

    redis = RedisClient.instance()
    await redis.ping()
    logger.info("Redis connection established at %s", settings.redis_url)

    # Engine pool and bot are wired in later phases.
    app.state.engine_pool = None
    app.state.bot = None

    try:
        yield
    finally:
        if app.state.engine_pool is not None:
            await app.state.engine_pool.shutdown()
        if app.state.bot is not None:
            await app.state.bot.shutdown()
        await redis.close()
        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Telegram Chess Bot API",
        version=__version__,
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)

    app.include_router(auth_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        redis = RedisClient.instance()
        ok = await redis.ping()
        return {"status": "ok" if ok else "degraded", "version": __version__}

    return app


app = create_app()
