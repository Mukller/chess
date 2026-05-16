from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.config import get_settings

router = Router(name="chess-handlers")


WELCOME_TEXT = (
    "♟️ <b>Telegram Chess Bot</b>\n\n"
    "Сыграйте партию против Stockfish прямо в Telegram.\n"
    "Нажмите кнопку ниже, чтобы открыть доску в WebApp."
)

HELP_TEXT = (
    "<b>Команды</b>\n"
    "/play — открыть доску и начать партию\n"
    "/help — показать это сообщение\n\n"
    "Доска работает в Telegram WebApp. Уровень сложности и цвет фигур "
    "выбираются на стартовом экране."
)


def _play_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    webapp_url = settings.telegram_webapp_url or "https://example.com"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="♟️ Играть",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=_play_keyboard(), parse_mode="HTML")


@router.message(Command("play"))
async def play_handler(message: Message) -> None:
    await message.answer(
        "Открываю доску…",
        reply_markup=_play_keyboard(),
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.message(F.text)
async def fallback_handler(message: Message) -> None:
    await message.answer(
        "Я отвечаю на /start, /play и /help. Нажмите кнопку, чтобы открыть доску.",
        reply_markup=_play_keyboard(),
    )
