import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth.routes import router as auth_router
from app.bot.bot import TelegramBot
from app.config import get_settings
from app.engine.pool import EnginePool
from app.game.routes import router as game_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.storage.redis_client import RedisClient
from app.ws.gateway import router as ws_router


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
    logger.info("Redis ready at %s", settings.redis_url)

    engine_pool = EnginePool.from_settings()
    try:
        await engine_pool.start()
        app.state.engine_pool = engine_pool
    except FileNotFoundError:
        logger.error(
            "Stockfish missing at %s — engine endpoints will respond with 503",
            settings.stockfish_path,
        )
        app.state.engine_pool = None

    bot = TelegramBot()
    await bot.start()
    app.state.bot = bot

    try:
        yield
    finally:
        if app.state.bot is not None:
            await app.state.bot.shutdown()
        if app.state.engine_pool is not None:
            await app.state.engine_pool.shutdown()
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
    app.include_router(game_router)
    app.include_router(ws_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        redis = RedisClient.instance()
        ok = await redis.ping()
        return {
            "status": "ok" if ok else "degraded",
            "version": __version__,
            "engine_ready": getattr(app.state, "engine_pool", None) is not None,
            "bot_configured": getattr(app.state, "bot", None) is not None
            and app.state.bot.is_configured,
        }

    return app


app = create_app()
