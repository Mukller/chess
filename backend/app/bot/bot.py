import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import router as handlers_router
from app.config import get_settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Owns the aiogram bot + dispatcher and runs polling as a background task."""

    def __init__(self) -> None:
        settings = get_settings()
        self._token = settings.telegram_bot_token
        self._bot: Optional[Bot] = None
        self._dispatcher: Optional[Dispatcher] = None
        self._task: Optional[asyncio.Task] = None

    @property
    def is_configured(self) -> bool:
        return bool(self._token)

    async def start(self) -> None:
        if not self.is_configured:
            logger.warning("telegram_bot_token not set — Telegram bot polling disabled")
            return
        self._bot = Bot(
            token=self._token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._dispatcher = Dispatcher()
        self._dispatcher.include_router(handlers_router)
        self._task = asyncio.create_task(self._run_polling(), name="telegram-bot-polling")
        logger.info("telegram bot polling started")

    async def _run_polling(self) -> None:
        assert self._bot is not None and self._dispatcher is not None
        try:
            await self._dispatcher.start_polling(
                self._bot,
                allowed_updates=self._dispatcher.resolve_used_update_types(),
            )
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("telegram polling stopped with error")

    async def shutdown(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._dispatcher is not None:
            await self._dispatcher.shutdown()
        if self._bot is not None:
            await self._bot.session.close()
        self._task = None
        self._dispatcher = None
        self._bot = None
        logger.info("telegram bot shutdown complete")
