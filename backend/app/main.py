import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.bot.bot import TelegramBot
from app.config import get_settings
from app.engine.pool import EnginePool
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
    logger.info("Redis ready at %s", settings.redis_url)

    engine_pool = EnginePool.from_settings()
    try:
        await engine_pool.start()
        app.state.engine_pool = engine_pool
        logger.info("Stockfish engine pool started")
    except FileNotFoundError:
        logger.error(
            "Stockfish missing at %s — bot will not work",
            settings.stockfish_path,
        )
        raise

    bot = TelegramBot(engine_pool=app.state.engine_pool)
    await bot.start()
    app.state.bot = bot
    logger.info("Telegram bot started")

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
        title="Telegram Chess Bot",
        version=__version__,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    return app


app = create_app()
