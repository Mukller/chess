import logging
import random
import time
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import chess

from app.game.service import GameService, IllegalMoveError, GameAlreadyFinishedError
from app.game.models import Color, Difficulty, GameStatus
from app.game.stats import StatsService, OPPONENT_ELO
from app.game.history import HistoryService, GameHistoryEntry, now_msk_iso
from app.game.online import OnlineService

logger = logging.getLogger(__name__)
router = Router(name="chess-handlers")

# =================== MESSAGE REPLY BUTTONS ===================

def _get_message_keyboard(message_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for message reply options."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_{message_id}"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{message_id}"),
        ],
        [
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_{message_id}"),
        ]
    ])


def _get_topic_name(user) -> str:
    """Get forum topic name from user (username or ID)."""
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"User {user.id}"


# =================== PIECE GLYPHS (both colours) ===================
# Standard Unicode chess pieces — outlined for white, filled for black.
PIECE_GLYPHS = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}

# =================== CELL BACKGROUNDS / HIGHLIGHTS ===================
EMPTY_LIGHT = "·"
EMPTY_DARK = " "
HL_SELECTED = "🟦"
HL_MOVE_LIGHT = "🟢"
HL_MOVE_DARK = "🟢"
HL_CAPTURE = "🟥"

FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]

# =================== BUTTONS ===================
BTN_PLAY = "♟️ Играть с ботом"
BTN_HOTSEAT = "👥 Двое на одном"
BTN_ONLINE = "🌐 Онлайн PvP"
BTN_PROFILE = "👤 Профиль"
BTN_HELP = "❓ Помощь"
BTN_STOP = "🛑 Остановить игру"
BTN_BACK = "⬅️ Назад"

BTN_DIFF_BEGINNER = "🐣 Новичок"
BTN_DIFF_EASY     = "1️⃣ Лёгкий"
BTN_DIFF_CASUAL   = "2️⃣ Простой"
BTN_DIFF_MEDIUM   = "3️⃣ Средний"
BTN_DIFF_ADVANCED = "4️⃣ Продвинутый"
BTN_DIFF_HARD     = "5️⃣ Сложный"
BTN_DIFF_EXPERT   = "6️⃣ Эксперт"
BTN_DIFF_MASTER   = "👑 Гроссмейстер"

BTN_COLOR_WHITE = "⚪ Белые"
BTN_COLOR_BLACK = "⚫ Чёрные"
BTN_COLOR_RANDOM = "🎲 Случайно"

BTN_HISTORY = "📜 История игр"
BTN_RESET_STATS = "🗑 Сбросить статистику"

BTN_ONLINE_HOST = "🆕 Создать игру"
BTN_ONLINE_JOIN = "🔑 Ввести код"

BOARD_HINT = (
    "<b>Как ходить:</b>\n"
    "1. Нажмите свою фигуру — подсветятся возможные ходы.\n"
    "2. Нажмите клетку назначения — ход выполнится.\n"
    "   • 🟦 — выбранная фигура\n"
    "   • 🟢 — возможный ход\n"
    "   • 🟥 — возможное взятие"
)


DIFFICULTY_BTN_MAP = {
    BTN_DIFF_BEGINNER: Difficulty.BEGINNER,
    BTN_DIFF_EASY:     Difficulty.EASY,
    BTN_DIFF_CASUAL:   Difficulty.CASUAL,
    BTN_DIFF_MEDIUM:   Difficulty.MEDIUM,
    BTN_DIFF_ADVANCED: Difficulty.ADVANCED,
    BTN_DIFF_HARD:     Difficulty.HARD,
    BTN_DIFF_EXPERT:   Difficulty.EXPERT,
    BTN_DIFF_MASTER:   Difficulty.MASTER,
}


class GameState(StatesGroup):
    selecting_difficulty = State()
    selecting_color = State()
    game_in_progress = State()
    hotseat_in_progress = State()
    online_menu = State()
    online_waiting_code = State()
    online_in_progress = State()


# =================== KEYBOARDS ===================

def _main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_PLAY), KeyboardButton(text=BTN_HOTSEAT)],
            [KeyboardButton(text=BTN_ONLINE), KeyboardButton(text=BTN_PROFILE)],
            [KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
    )


def _difficulty_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_DIFF_BEGINNER), KeyboardButton(text=BTN_DIFF_EASY)],
            [KeyboardButton(text=BTN_DIFF_CASUAL),   KeyboardButton(text=BTN_DIFF_MEDIUM)],
            [KeyboardButton(text=BTN_DIFF_ADVANCED), KeyboardButton(text=BTN_DIFF_HARD)],
            [KeyboardButton(text=BTN_DIFF_EXPERT),   KeyboardButton(text=BTN_DIFF_MASTER)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def _color_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_COLOR_WHITE), KeyboardButton(text=BTN_COLOR_BLACK)],
            [KeyboardButton(text=BTN_COLOR_RANDOM)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def _game_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_STOP)]],
        resize_keyboard=True,
    )


def _profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_HISTORY)],
            [KeyboardButton(text=BTN_RESET_STATS)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def _online_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ONLINE_HOST), KeyboardButton(text=BTN_ONLINE_JOIN)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


# =================== BOARD RENDER ===================

def _is_light(square: int) -> bool:
    return (chess.square_file(square) + chess.square_rank(square)) % 2 == 1


def _empty_label(square: int) -> str:
    return EMPTY_LIGHT if _is_light(square) else EMPTY_DARK


def _piece_glyph(piece: chess.Piece) -> str:
    return PIECE_GLYPHS.get(piece.symbol(), piece.symbol())


def _square_label(piece, square, is_selected, is_target_empty, is_target_capture) -> str:
    if is_selected:
        return HL_SELECTED
    if is_target_capture:
        return HL_CAPTURE
    if is_target_empty:
        return HL_MOVE_LIGHT if _is_light(square) else HL_MOVE_DARK
    if piece is None:
        return _empty_label(square)
    return _piece_glyph(piece)


def _board_keyboard(fen: str, perspective: Color, selected_square: str | None = None) -> InlineKeyboardMarkup:
    """8x8 board, no labels. `perspective` controls flip — bottom row is that side."""
    board = chess.Board(fen)
    flip = perspective == Color.BLACK

    targets: set[int] = set()
    selected_idx: int | None = None
    if selected_square:
        try:
            selected_idx = chess.parse_square(selected_square)
            for move in board.legal_moves:
                if move.from_square == selected_idx:
                    targets.add(move.to_square)
        except ValueError:
            selected_idx = None

    rows: list[list[InlineKeyboardButton]] = []
    file_order = list(reversed(FILES)) if flip else FILES
    rank_order = range(1, 9) if flip else range(8, 0, -1)

    for rank in rank_order:
        row = []
        for f in file_order:
            sq = chess.parse_square(f + str(rank))
            piece = board.piece_at(sq)
            is_selected = sq == selected_idx
            is_target = sq in targets
            is_target_capture = is_target and piece is not None
            is_target_empty = is_target and piece is None
            label = _square_label(piece, sq, is_selected, is_target_empty, is_target_capture)
            row.append(InlineKeyboardButton(text=label, callback_data=f"sq:{f}{rank}"))
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _safe_edit_markup(callback: CallbackQuery, markup: InlineKeyboardMarkup) -> None:
    """Edit the inline keyboard, ignoring 'message is not modified' errors and minor rerender hiccups."""
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        logger.warning("edit_reply_markup failed: %s", e)


async def _safe_edit_text(callback: CallbackQuery, text: str, markup: InlineKeyboardMarkup | None = None) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        logger.warning("edit_text failed: %s", e)


# =================== HELPERS ===================

DIFFICULTY_NAMES = {
    Difficulty.BEGINNER: "Новичок",
    Difficulty.EASY:     "Лёгкий",
    Difficulty.CASUAL:   "Простой",
    Difficulty.MEDIUM:   "Средний",
    Difficulty.ADVANCED: "Продвинутый",
    Difficulty.HARD:     "Сложный",
    Difficulty.EXPERT:   "Эксперт",
    Difficulty.MASTER:   "Гроссмейстер",
}


def _difficulty_text(d: Difficulty) -> str:
    return DIFFICULTY_NAMES.get(d, "—")


def _color_text(c: Color) -> str:
    return "белые" if c == Color.WHITE else "чёрные"


def _format_profile(stats) -> str:
    win_rate = (stats.wins / stats.games_played * 100) if stats.games_played else 0.0
    lines = [
        "<b>👤 Профиль</b>",
        "",
        f"<b>ELO рейтинг</b>",
        f"🏆 Текущий: <code>{stats.elo}</code>",
        f"🎖 Рекорд: <code>{stats.peak_elo}</code>",
        "",
        f"<b>Статистика</b>",
        f"🎮 Всего партий: <code>{stats.games_played}</code>",
        f"✅ Побед: <code>{stats.wins}</code>",
        f"❌ Поражений: <code>{stats.losses}</code>",
        f"🤝 Ничьих: <code>{stats.draws}</code>",
        f"📈 Винрейт: <code>{win_rate:.1f}%</code>",
    ]
    if stats.by_difficulty:
        lines.append("")
        lines.append("<b>По уровням сложности</b>")
        for d in Difficulty:
            ds = stats.by_difficulty.get(d.value)
            if ds and ds.played > 0:
                lines.append(
                    f"  • {DIFFICULTY_NAMES[d]}: <code>{ds.played}</code> п. (В:{ds.wins} П:{ds.losses} Н:{ds.draws})"
                )
    return "\n".join(lines)


def _result_emoji(result: str) -> str:
    return {"win": "🏆", "loss": "💔", "draw": "🤝", "aborted": "🏁"}.get(result, "•")


def _result_text(result: str) -> str:
    return {"win": "Победа", "loss": "Поражение", "draw": "Ничья", "aborted": "Прервана"}.get(result, "—")


def _safe_difficulty_label(value: str) -> str:
    try:
        return _difficulty_text(Difficulty(value))
    except Exception:
        return value


def _format_history_list(entries, total: int) -> tuple[str, InlineKeyboardMarkup]:
    if not entries:
        return ("📜 <b>История игр</b>\n\n<i>Пусто — сыграйте первую партию!</i>",
                InlineKeyboardMarkup(inline_keyboard=[]))
    lines = [f"<b>📜 История игр</b> — всего: <code>{total}</code>", ""]
    rows: list[list[InlineKeyboardButton]] = []
    for i, e in enumerate(entries, 1):
        diff = _safe_difficulty_label(e.difficulty)
        color_t = "♔" if e.user_color == Color.WHITE.value else "♚"
        lines.append(
            f"{i}. {_result_emoji(e.result)} <b>{_result_text(e.result)}</b> {color_t} {diff} · {len(e.moves_uci)} ходов"
        )
        rows.append([InlineKeyboardButton(
            text=f"#{i} {_result_emoji(e.result)} {diff}",
            callback_data=f"hist:{e.game_id}",
        )])
    return "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


def _format_history_entry(e: GameHistoryEntry) -> str:
    diff = _safe_difficulty_label(e.difficulty)
    color_t = "♔ Белые" if e.user_color == Color.WHITE.value else "♚ Чёрные"
    duration = ""
    try:
        from datetime import datetime
        s = datetime.strptime(e.started_at, "%Y-%m-%d %H:%M:%S")
        f = datetime.strptime(e.finished_at, "%Y-%m-%d %H:%M:%S")
        secs = int((f - s).total_seconds())
        duration = f"⏱️ <code>{secs // 60}:{secs % 60:02d}</code>\n"
    except Exception:
        pass
    moves_block = ""
    if e.moves_uci:
        rendered = []
        for i in range(0, len(e.moves_uci), 2):
            num = i // 2 + 1
            w = e.moves_uci[i]
            b = e.moves_uci[i + 1] if i + 1 < len(e.moves_uci) else ""
            rendered.append(f"{num}. {w} {b}".strip())
        moves_block = "\n\n<b>📝 Ходы</b>\n<code>" + " ".join(rendered) + "</code>"
    return (
        f"<b>{_result_emoji(e.result)} {_result_text(e.result)}</b>\n"
        f"\n<b>📊 Информация</b>\n"
        f"🎯 Уровень: <code>{diff}</code>\n"
        f"♟️ Фигуры: <code>{color_t}</code>\n"
        f"📍 Ходов: <code>{len(e.moves_uci)}</code>\n"
        f"{duration}"
        f"\n<b>⏰ Время</b>\n"
        f"🕐 Начало: <code>{e.started_at}</code>\n"
        f"🏁 Конец: <code>{e.finished_at}</code>\n"
        f"\n<b>📈 Рейтинг</b>\n"
        f"Было: <code>{e.elo_before}</code> → Стало: <code>{e.elo_after}</code> ({e.elo_delta:+d})"
        f"{moves_block}"
    )


def _restore_user_color(value) -> Color:
    if isinstance(value, Color):
        return value
    if isinstance(value, str):
        try:
            return Color(value)
        except Exception:
            return Color.WHITE if value.lower().startswith("w") else Color.BLACK
    return Color.WHITE


def _restore_difficulty(value) -> Difficulty:
    if isinstance(value, Difficulty):
        return value
    if isinstance(value, str):
        try:
            return Difficulty(value)
        except Exception:
            pass
    return Difficulty.MEDIUM


# =================== FORUM TOPIC MESSAGE HANDLER ===================

@router.message(F.chat.type.in_(("group", "supergroup")))
async def group_message_handler(message: Message, bot: Bot) -> None:
    """Handle incoming messages in the group - just log them."""
    try:
        # Skip messages from bot itself
        if message.from_user.is_bot:
            return

        # Skip service messages (joins, leaves, etc.)
        if message.content_type != "text":
            return

        # Get the group chat ID from config
        from app.config import get_settings
        settings = get_settings()
        group_chat_id = settings.group_chat_id

        # Only process messages in the configured group
        if message.chat.id != group_chat_id:
            return

        user = message.from_user
        username = user.username or user.first_name or str(user.id)

        logger.info(f"Group message from {username}: {message.text}")

    except Exception as e:
        logger.exception(f"Error in group_message_handler: {e}")


@router.callback_query(F.data.startswith("reply_"))
async def reply_callback_handler(callback: CallbackQuery) -> None:
    """Handle reply button click."""
    try:
        message_id = callback.data.split("_", 1)[1]
        await callback.answer(
            f"Ответ на сообщение #{message_id}",
            show_alert=False
        )
        # TODO: Implement reply functionality
    except Exception as e:
        logger.exception(f"Error in reply handler: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("edit_"))
async def edit_callback_handler(callback: CallbackQuery) -> None:
    """Handle edit button click."""
    try:
        message_id = callback.data.split("_", 1)[1]
        await callback.answer(
            f"Редактирование сообщения #{message_id}",
            show_alert=False
        )
        # TODO: Implement edit functionality
    except Exception as e:
        logger.exception(f"Error in edit handler: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("delete_"))
async def delete_callback_handler(callback: CallbackQuery) -> None:
    """Handle delete button click."""
    try:
        message_id = callback.data.split("_", 1)[1]
        # Delete the message from the topic
        await callback.message.delete()
        await callback.answer("✅ Сообщение удалено", show_alert=False)
    except Exception as e:
        logger.exception(f"Error in delete handler: {e}")
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


# =================== /START + MAIN MENU ===================

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "<b>♟️ Telegram Chess Bot</b>\n\n"
        "Выберите режим игры:\n"
        "  • <b>Играть с ботом</b> — Stockfish, 8 уровней\n"
        "  • <b>Двое на одном</b> — на одном устройстве\n"
        "  • <b>Онлайн PvP</b> — с другом по коду\n\n"
        "Другое:\n"
        "  • <b>Профиль</b> — статистика и рейтинг\n"
        "  • <b>Помощь</b> — справка"
    )
    await message.answer(text, reply_markup=_main_keyboard(), parse_mode="HTML")


@router.message(F.text == BTN_HELP)
async def help_handler(message: Message) -> None:
    text = (
        "<b>❓ Помощь</b>\n\n"
        "<b>🎮 Режимы игры</b>\n"
        "  • <b>Играть с ботом</b> — 8 уровней (Новичок → Гроссмейстер)\n"
        "  • <b>Двое на одном</b> — по очереди на одном устройстве\n"
        "  • <b>Онлайн PvP</b> — с другом по коду приглашения\n\n"
        "<b>♟️ Как ходить</b>\n"
        "  1. Нажмите свою фигуру → подсветятся ходы\n"
        "  2. Выберите клетку назначения\n"
        "  3. Ход выполнится\n\n"
        "<b>🎨 Обозначения клеток</b>\n"
        "  🟦 — выбранная фигура\n"
        "  🟢 — возможный ход\n"
        "  🟥 — взятие фигуры\n\n"
        "<b>♔ Фигуры</b>\n"
        "Белые: ♔ ♕ ♖ ♗ ♘ ♙\n"
        "Чёрные: ♚ ♛ ♜ ♝ ♞ ♟"
    )
    await message.answer(text, reply_markup=_main_keyboard(), parse_mode="HTML")


# =================== PROFILE / HISTORY ===================

@router.message(F.text == BTN_PROFILE)
async def profile_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    stats = await StatsService().get(message.from_user.id)
    await message.answer(_format_profile(stats), reply_markup=_profile_keyboard(), parse_mode="HTML")


@router.message(F.text == BTN_RESET_STATS)
async def reset_stats_handler(message: Message) -> None:
    stats = await StatsService().reset(message.from_user.id)
    await message.answer(
        "<b>♻️ Статистика сброшена</b>\n\n" + _format_profile(stats),
        reply_markup=_profile_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_HISTORY)
async def history_handler(message: Message) -> None:
    history = HistoryService()
    user_id = message.from_user.id
    entries = await history.list_recent(user_id, limit=10)
    total = await history.count(user_id)
    text, markup = _format_history_list(entries, total)
    await message.answer(text, reply_markup=_profile_keyboard(), parse_mode="HTML")
    if entries:
        await message.answer("<b>Выберите партию для просмотра:</b>", reply_markup=markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("hist:"))
async def history_entry_handler(callback: CallbackQuery) -> None:
    game_id = callback.data.split(":", 1)[1]
    entry = await HistoryService().get(game_id, callback.from_user.id)
    if not entry:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    await callback.message.answer(_format_history_entry(entry), parse_mode="HTML")
    await callback.answer()


# =================== AI: SELECT DIFFICULTY + COLOR ===================

@router.message(F.text == BTN_PLAY)
async def play_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(GameState.selecting_difficulty)
    lines = ["<b>🎯 Выберите уровень сложности</b>", ""]
    for d in Difficulty:
        lines.append(f"  • <b>{DIFFICULTY_NAMES[d]}</b> — <code>ELO ~{OPPONENT_ELO[d]}</code>")
    await message.answer("\n".join(lines), reply_markup=_difficulty_keyboard(), parse_mode="HTML")


@router.message(GameState.selecting_difficulty, F.text.in_(set(DIFFICULTY_BTN_MAP.keys())))
async def difficulty_choice_handler(message: Message, state: FSMContext) -> None:
    difficulty = DIFFICULTY_BTN_MAP[message.text]
    await state.update_data(difficulty=difficulty.value)
    await state.set_state(GameState.selecting_color)
    text = (
        f"<b>🎯 Уровень выбран</b>\n"
        f"<code>{_difficulty_text(difficulty)}</code>\n\n"
        f"<b>♟️ Выберите цвет фигур</b>\n\n"
        f"⚪ <b>Белые</b> — вы ходите первым\n"
        f"⚫ <b>Чёрные</b> — компьютер ходит первым\n"
        f"🎲 <b>Случайно</b>"
    )
    await message.answer(text, reply_markup=_color_keyboard(), parse_mode="HTML")


@router.message(F.text == BTN_BACK)
async def back_universal_handler(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current == GameState.selecting_color.state:
        await state.set_state(GameState.selecting_difficulty)
        await message.answer("<b>🎯 Выберите уровень сложности</b>", reply_markup=_difficulty_keyboard(), parse_mode="HTML")
        return
    await state.clear()
    await message.answer("<b>📋 Главное меню</b>", reply_markup=_main_keyboard(), parse_mode="HTML")


@router.message(GameState.selecting_color, F.text.in_({BTN_COLOR_WHITE, BTN_COLOR_BLACK, BTN_COLOR_RANDOM}))
async def color_choice_handler(message: Message, state: FSMContext, engine_pool=None) -> None:
    if message.text == BTN_COLOR_RANDOM:
        color = random.choice([Color.WHITE, Color.BLACK])
    elif message.text == BTN_COLOR_WHITE:
        color = Color.WHITE
    else:
        color = Color.BLACK

    data = await state.get_data()
    difficulty = _restore_difficulty(data.get("difficulty"))
    user_id = message.from_user.id

    try:
        game_service = GameService()
        game_state = await game_service.start(
            user_id=user_id,
            difficulty=difficulty,
            user_color=color,
            engine_pool=engine_pool,
        )
    except Exception as e:
        logger.exception("Error starting game")
        await message.answer(f"❌ Ошибка: {e}", reply_markup=_main_keyboard())
        await state.clear()
        return

    await state.set_state(GameState.game_in_progress)
    await state.update_data(
        game_id=game_state.game_id,
        user_color=color.value,
        difficulty=difficulty.value,
        selected_square=None,
        started_at=now_msk_iso(),
    )

    await message.answer(
        f"<b>🎮 Партия началась!</b>\n\n"
        f"🎯 Уровень: <code>{_difficulty_text(difficulty)}</code>\n"
        f"♟️ Цвет: <code>{_color_text(color)}</code>",
        reply_markup=_game_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(BOARD_HINT, parse_mode="HTML", reply_markup=_board_keyboard(game_state.fen, color, None))


async def _persist_finished_game(user_id, state_data, final_state, result, elo_update=None) -> None:
    try:
        entry = GameHistoryEntry(
            game_id=final_state.game_id,
            user_id=user_id,
            difficulty=final_state.difficulty.value,
            user_color=final_state.user_color.value,
            status=final_state.status.value,
            result=result,
            started_at=state_data.get("started_at") or now_msk_iso(),
            finished_at=now_msk_iso(),
            moves_uci=list(final_state.moves),
            final_fen=final_state.fen,
            elo_before=elo_update.elo_before if elo_update else 0,
            elo_after=elo_update.elo_after if elo_update else 0,
            elo_delta=elo_update.delta if elo_update else 0,
        )
        await HistoryService().save(entry)
    except Exception:
        logger.exception("Failed to persist finished game")


@router.message(GameState.game_in_progress, F.text == BTN_STOP)
async def stop_game_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data.get("game_id")
    difficulty = _restore_difficulty(data.get("difficulty"))
    user_id = message.from_user.id

    delta_text = ""
    if game_id:
        try:
            current = await GameService().get(game_id, user_id)
            elo_update = await StatsService().record_result(user_id, difficulty, user_score=0.0)
            delta_text = f"\n📉 ELO: {elo_update.stats.elo} ({elo_update.delta:+d})"
            current.status = GameStatus.ABANDONED
            await _persist_finished_game(user_id, data, current, "aborted", elo_update)
        except Exception:
            logger.exception("Error stopping game")

    await state.clear()
    await message.answer(
        f"🏁 <b>Игра остановлена.</b>{delta_text}",
        reply_markup=_main_keyboard(),
        parse_mode="HTML",
    )


@router.message(GameState.hotseat_in_progress, F.text == BTN_STOP)
async def hotseat_stop_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏁 <b>Hot-seat партия остановлена.</b>", reply_markup=_main_keyboard(), parse_mode="HTML")


@router.message(GameState.online_in_progress, F.text == BTN_STOP)
async def online_stop_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data.get("online_game_id")
    if game_id:
        await OnlineService().abort(game_id, message.from_user.id)
    await state.clear()
    await message.answer("🏁 <b>Онлайн партия остановлена.</b>", reply_markup=_main_keyboard(), parse_mode="HTML")


@router.message(F.text == BTN_STOP)
async def stop_no_game_handler(message: Message) -> None:
    await message.answer("<b>⚠️ Нет активной партии</b>", reply_markup=_main_keyboard(), parse_mode="HTML")


# =================== AI: SQUARE CLICK (board callback) ===================

@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()


async def _route_square_callback(callback: CallbackQuery, state: FSMContext, engine_pool):
    """Dispatch a square click to the right handler based on current FSM state."""
    current = await state.get_state()
    if current == GameState.hotseat_in_progress.state:
        await _hotseat_square_handler(callback, state)
    elif current == GameState.online_in_progress.state:
        await _online_square_handler(callback, state)
    else:
        await _ai_square_handler(callback, state, engine_pool)


@router.callback_query(F.data.startswith("sq:"))
async def square_dispatcher(callback: CallbackQuery, state: FSMContext, engine_pool=None) -> None:
    try:
        await _route_square_callback(callback, state, engine_pool)
    except Exception as e:
        logger.exception("square dispatch error")
        try:
            await callback.answer(f"❌ {e}", show_alert=True)
        except Exception:
            pass


async def _ai_square_handler(callback: CallbackQuery, state: FSMContext, engine_pool):
    square = callback.data.split(":", 1)[1]
    data = await state.get_data()
    game_id = data.get("game_id")
    user_id = callback.from_user.id
    user_color = _restore_user_color(data.get("user_color"))
    difficulty = _restore_difficulty(data.get("difficulty"))
    selected_square = data.get("selected_square")

    if not game_id:
        await callback.answer("❌ Игра не инициализирована", show_alert=True)
        return

    game_service = GameService()
    try:
        current = await game_service.get(game_id, user_id)
    except Exception as e:
        logger.exception("Error fetching game state")
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
        return

    board = chess.Board(current.fen)

    if selected_square is None:
        try:
            sq_idx = chess.parse_square(square)
        except ValueError:
            await callback.answer()
            return
        piece = board.piece_at(sq_idx)
        if piece is None:
            await callback.answer("Пустая клетка")
            return
        user_is_white = user_color == Color.WHITE
        if (piece.color == chess.WHITE) != user_is_white:
            await callback.answer("Это не ваша фигура")
            return
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(current.fen, user_color, square))
        await callback.answer()
        return

    if selected_square == square:
        await state.update_data(selected_square=None)
        await _safe_edit_markup(callback, _board_keyboard(current.fen, user_color, None))
        await callback.answer("Отмена выбора")
        return

    try:
        from_idx = chess.parse_square(selected_square)
        to_idx = chess.parse_square(square)
    except ValueError:
        await state.update_data(selected_square=None)
        await callback.answer()
        return

    piece_at_target = board.piece_at(to_idx)
    user_is_white = user_color == Color.WHITE
    if piece_at_target is not None and (piece_at_target.color == chess.WHITE) == user_is_white:
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(current.fen, user_color, square))
        await callback.answer()
        return

    move_uci = selected_square + square
    piece = board.piece_at(from_idx)
    if piece and piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(to_idx)
        if (user_is_white and to_rank == 7) or (not user_is_white and to_rank == 0):
            move_uci += "q"

    try:
        outcome = await game_service.make_move(game_id, user_id, move_uci, engine_pool=engine_pool)
    except IllegalMoveError:
        await callback.answer("❌ Некорректный ход")
        await state.update_data(selected_square=None)
        await _safe_edit_markup(callback, _board_keyboard(current.fen, user_color, None))
        return
    except GameAlreadyFinishedError:
        await callback.answer("Игра уже завершена")
        await state.clear()
        return
    except Exception as e:
        logger.exception("Error making move")
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
        return

    game_state = outcome.state
    engine_move = outcome.engine_move_san or outcome.engine_move_uci or "—"

    status_text = ""
    user_score = None
    keep_playing = True
    result_label = None
    user_is_white = user_color == Color.WHITE

    if game_state.status == GameStatus.CHECKMATE:
        loser_white = chess.Board(game_state.fen).turn == chess.WHITE
        user_lost = (loser_white and user_is_white) or (not loser_white and not user_is_white)
        if user_lost:
            status_text = "\n💔 <b>Мат! Вы проиграли.</b>"
            user_score = 0.0
            result_label = "loss"
        else:
            status_text = "\n🏆 <b>Мат! Вы выиграли!</b>"
            user_score = 1.0
            result_label = "win"
        keep_playing = False
    elif game_state.status == GameStatus.STALEMATE:
        status_text = "\n🤝 <b>Пат! Ничья.</b>"
        user_score = 0.5
        result_label = "draw"
        keep_playing = False
    elif game_state.status == GameStatus.DRAW:
        status_text = "\n🤝 <b>Ничья!</b>"
        user_score = 0.5
        result_label = "draw"
        keep_playing = False

    elo_update = None
    if user_score is not None:
        try:
            elo_update = await StatsService().record_result(user_id, difficulty, user_score)
            sign = "📈" if elo_update.delta > 0 else ("📉" if elo_update.delta < 0 else "📊")
            status_text += f"\n{sign} ELO: <b>{elo_update.stats.elo}</b> ({elo_update.delta:+d})"
        except Exception:
            logger.exception("Error recording stats")
        await _persist_finished_game(user_id, data, game_state, result_label or "draw", elo_update)

    await state.update_data(selected_square=None)

    # Always include a move counter so message text is unique → edit_text always succeeds
    move_no = len(game_state.moves)
    text = (
        f"<b>♟️ Ход №{move_no}</b>\n"
        f"👤 Вы: <code>{move_uci}</code>\n"
        f"🤖 Бот: <code>{engine_move}</code>"
        f"{status_text}"
    )

    if keep_playing:
        await _safe_edit_text(callback, text, _board_keyboard(game_state.fen, user_color, None))
    else:
        await state.clear()
        await _safe_edit_text(callback, text)
        await callback.message.answer(
            "<b>🎮 Партия завершена</b>\n\nВыберите режим для новой игры:",
            reply_markup=_main_keyboard(),
            parse_mode="HTML",
        )
    await callback.answer()


# =================== HOT-SEAT MODE ===================

@router.message(F.text == BTN_HOTSEAT)
async def hotseat_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    fen = chess.STARTING_FEN
    await state.set_state(GameState.hotseat_in_progress)
    await state.update_data(
        hs_fen=fen,
        hs_moves=[],
        hs_turn="white",
        selected_square=None,
        started_at=now_msk_iso(),
    )
    await message.answer(
        "<b>👥 Hot-seat игра</b>\n\n"
        "Ходы по очереди на одном устройстве\n\n"
        "Сейчас ходят: <code>♔ Белые</code>",
        reply_markup=_game_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(BOARD_HINT, parse_mode="HTML", reply_markup=_board_keyboard(fen, Color.WHITE, None))


async def _hotseat_square_handler(callback: CallbackQuery, state: FSMContext) -> None:
    square = callback.data.split(":", 1)[1]
    data = await state.get_data()
    fen = data.get("hs_fen") or chess.STARTING_FEN
    turn = data.get("hs_turn", "white")
    selected_square = data.get("selected_square")
    moves: list = list(data.get("hs_moves") or [])

    board = chess.Board(fen)
    perspective = Color.WHITE  # Always show board from white's perspective (no flip)

    if selected_square is None:
        try:
            sq_idx = chess.parse_square(square)
        except ValueError:
            await callback.answer()
            return
        piece = board.piece_at(sq_idx)
        if piece is None:
            await callback.answer("Пустая клетка")
            return
        side_is_white = piece.color == chess.WHITE
        if (turn == "white") != side_is_white:
            await callback.answer("Сейчас ход другой стороны")
            return
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(fen, perspective, square))
        await callback.answer()
        return

    if selected_square == square:
        await state.update_data(selected_square=None)
        await _safe_edit_markup(callback, _board_keyboard(fen, perspective, None))
        await callback.answer("Отмена выбора")
        return

    try:
        from_idx = chess.parse_square(selected_square)
        to_idx = chess.parse_square(square)
    except ValueError:
        await state.update_data(selected_square=None)
        await callback.answer()
        return

    piece_at_target = board.piece_at(to_idx)
    side_white = turn == "white"
    if piece_at_target is not None and (piece_at_target.color == chess.WHITE) == side_white:
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(fen, perspective, square))
        await callback.answer()
        return

    move_uci = selected_square + square
    piece = board.piece_at(from_idx)
    if piece and piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(to_idx)
        if (side_white and to_rank == 7) or (not side_white and to_rank == 0):
            move_uci += "q"

    try:
        move = chess.Move.from_uci(move_uci)
    except Exception:
        await callback.answer("❌ Некорректный ход")
        return
    if move not in board.legal_moves:
        await callback.answer("❌ Нелегальный ход")
        await state.update_data(selected_square=None)
        await _safe_edit_markup(callback, _board_keyboard(fen, perspective, None))
        return

    board.push(move)
    moves.append(move.uci())
    new_fen = board.fen()
    new_turn = "black" if turn == "white" else "white"
    new_perspective = Color.WHITE  # Always show board from white's perspective (no flip)

    status_text = ""
    keep_playing = True
    if board.is_checkmate():
        winner = "Белые" if turn == "white" else "Чёрные"
        status_text = f"\n🏆 <b>Мат! Победили {winner.lower()}!</b>"
        keep_playing = False
    elif board.is_stalemate():
        status_text = "\n🤝 <b>Пат! Ничья.</b>"
        keep_playing = False
    elif board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        status_text = "\n🤝 <b>Ничья.</b>"
        keep_playing = False

    await state.update_data(
        hs_fen=new_fen,
        hs_moves=moves,
        hs_turn=new_turn,
        selected_square=None,
    )

    move_no = len(moves)
    side_label = "Белые" if turn == "white" else "Чёрные"
    next_label = "♔ Белые" if new_turn == "white" else "♚ Чёрные"
    text = (
        f"<b>♟️ Ход №{move_no}</b>\n"
        f"{side_label}: <code>{move_uci}</code>\n"
        f"Сейчас: <code>{next_label}</code>"
        f"{status_text}"
    )

    if keep_playing:
        await _safe_edit_text(callback, text, _board_keyboard(new_fen, new_perspective, None))
    else:
        await state.clear()
        await _safe_edit_text(callback, text)
        await callback.message.answer("<b>🎮 Партия завершена</b>\n\nГлавное меню:", reply_markup=_main_keyboard(), parse_mode="HTML")
    await callback.answer()


# =================== ONLINE PvP (scaffolding) ===================

@router.message(F.text == BTN_ONLINE)
async def online_menu_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(GameState.online_menu)
    text = (
        "<b>🌐 Онлайн PvP</b>\n\n"
        "• <b>Создать игру</b> — вы получите код для друга\n"
        "• <b>Ввести код</b> — присоединитесь к игре\n\n"
        "<i>⚠️ Live-режим в бете: ходы подгружаются по клику</i>"
    )
    await message.answer(text, reply_markup=_online_menu_keyboard(), parse_mode="HTML")


@router.message(GameState.online_menu, F.text == BTN_ONLINE_HOST)
async def online_host_handler(message: Message, state: FSMContext) -> None:
    color = random.choice([Color.WHITE, Color.BLACK])
    user = message.from_user
    game = await OnlineService().create(user.id, user.username or user.full_name or str(user.id), color)
    await state.set_state(GameState.online_in_progress)
    await state.update_data(
        online_game_id=game.game_id,
        online_code=game.code,
        online_role="host",
        selected_square=None,
        started_at=now_msk_iso(),
    )
    color_label = "белыми" if color == Color.WHITE else "чёрными"
    await message.answer(
        f"<b>🌐 Игра создана!</b>\n\n"
        f"Код игры: <code>{game.code}</code>\n"
        f"Цвет: <code>{color_label}</code>\n\n"
        f"Передайте код другу. Когда он присоединится, доска оживёт.\n"
        f"Нажмите на доску, чтобы обновить состояние.",
        reply_markup=_game_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(BOARD_HINT, parse_mode="HTML", reply_markup=_board_keyboard(game.fen, color, None))


@router.message(GameState.online_menu, F.text == BTN_ONLINE_JOIN)
async def online_join_prompt_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(GameState.online_waiting_code)
    await message.answer(
        "<b>🌐 Ввод кода игры</b>\n\n"
        "Введите 6-значный код от хоста:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=BTN_BACK)]],
            resize_keyboard=True,
        ),
        parse_mode="HTML",
    )


@router.message(GameState.online_waiting_code, F.text & ~F.text.in_({BTN_BACK}))
async def online_join_handler(message: Message, state: FSMContext) -> None:
    code = (message.text or "").strip().upper()
    if not code or len(code) > 12:
        await message.answer("Код должен быть коротким. Попробуйте ещё раз.")
        return
    user = message.from_user
    game = await OnlineService().join(code, user.id, user.username or user.full_name or str(user.id))
    if not game:
        await message.answer(
            "❌ Код не найден или игра уже занята. Проверьте код и попробуйте снова.",
            reply_markup=_online_menu_keyboard(),
        )
        await state.set_state(GameState.online_menu)
        return
    my_color = game.color_for_user(user.id)
    if my_color is None:
        await message.answer("❌ Не удалось определить цвет. Попробуйте позже.", reply_markup=_main_keyboard())
        await state.clear()
        return
    await state.set_state(GameState.online_in_progress)
    await state.update_data(
        online_game_id=game.game_id,
        online_code=game.code,
        online_role="guest",
        selected_square=None,
        started_at=now_msk_iso(),
    )
    label = "белыми" if my_color == Color.WHITE else "чёрными"
    await message.answer(
        f"<b>🌐 Вы присоединились!</b>\n\n"
        f"Код: <code>{game.code}</code>\n"
        f"Соперник: <code>{game.host_username or 'host'}</code>\n"
        f"Цвет: <code>{label}</code>",
        reply_markup=_game_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(BOARD_HINT, parse_mode="HTML", reply_markup=_board_keyboard(game.fen, my_color, None))


async def _online_square_handler(callback: CallbackQuery, state: FSMContext) -> None:
    square = callback.data.split(":", 1)[1]
    data = await state.get_data()
    game_id = data.get("online_game_id")
    if not game_id:
        await callback.answer("❌ Игра не найдена. Создайте новую.", show_alert=True)
        return

    service = OnlineService()
    game = await service.get(game_id)
    if not game:
        await callback.answer("❌ Игра не найдена в базе.", show_alert=True)
        return

    user_id = callback.from_user.id
    my_color = game.color_for_user(user_id)
    if my_color is None:
        await callback.answer("Вы не участник этой игры")
        return

    if game.status == "waiting":
        await callback.answer("⏳ Ждём соперника...")
        return
    if game.status != "active":
        await callback.answer(f"Игра завершена: {game.status}", show_alert=True)
        return

    selected_square = data.get("selected_square")
    board = chess.Board(game.fen)

    if game.turn != my_color.value:
        await _safe_edit_markup(callback, _board_keyboard(game.fen, my_color, None))
        await callback.answer("Сейчас не ваш ход")
        return

    if selected_square is None:
        try:
            sq_idx = chess.parse_square(square)
        except ValueError:
            await callback.answer()
            return
        piece = board.piece_at(sq_idx)
        if piece is None:
            await callback.answer("Пустая клетка")
            return
        my_is_white = my_color == Color.WHITE
        if (piece.color == chess.WHITE) != my_is_white:
            await callback.answer("Это не ваша фигура")
            return
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(game.fen, my_color, square))
        await callback.answer()
        return

    if selected_square == square:
        await state.update_data(selected_square=None)
        await _safe_edit_markup(callback, _board_keyboard(game.fen, my_color, None))
        await callback.answer("Отмена выбора")
        return

    try:
        from_idx = chess.parse_square(selected_square)
        to_idx = chess.parse_square(square)
    except ValueError:
        await state.update_data(selected_square=None)
        await callback.answer()
        return

    piece_at_target = board.piece_at(to_idx)
    my_is_white = my_color == Color.WHITE
    if piece_at_target is not None and (piece_at_target.color == chess.WHITE) == my_is_white:
        await state.update_data(selected_square=square)
        await _safe_edit_markup(callback, _board_keyboard(game.fen, my_color, square))
        await callback.answer()
        return

    move_uci = selected_square + square
    piece = board.piece_at(from_idx)
    if piece and piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(to_idx)
        if (my_is_white and to_rank == 7) or (not my_is_white and to_rank == 0):
            move_uci += "q"

    updated, error = await service.apply_move(game_id, user_id, move_uci)
    if error:
        await callback.answer(f"❌ {error}")
        await state.update_data(selected_square=None)
        if updated:
            await _safe_edit_markup(callback, _board_keyboard(updated.fen, my_color, None))
        return

    await state.update_data(selected_square=None)
    status_line = ""
    keep_playing = True
    if updated.status == "checkmate":
        winner_color = "white" if updated.turn == "black" else "black"  # side that just moved
        winner_is_me = winner_color == my_color.value
        status_line = "\n🏆 <b>Мат! Вы выиграли!</b>" if winner_is_me else "\n💔 <b>Мат. Вы проиграли.</b>"
        keep_playing = False
    elif updated.status == "stalemate":
        status_line = "\n🤝 <b>Пат! Ничья.</b>"
        keep_playing = False
    elif updated.status == "draw":
        status_line = "\n🤝 <b>Ничья.</b>"
        keep_playing = False

    move_no = len(updated.moves)
    next_label = "белые" if updated.turn == "white" else "чёрные"
    text = (
        f"<b>♟️ Ход №{move_no}</b>\n\n"
        f"Ход: <code>{move_uci}</code>\n"
        f"Ходят: <code>{next_label}</code>"
        f"{status_line}"
    )

    if keep_playing:
        await _safe_edit_text(callback, text, _board_keyboard(updated.fen, my_color, None))
    else:
        await state.clear()
        await _safe_edit_text(callback, text)
        await callback.message.answer("Главное меню.", reply_markup=_main_keyboard())
    await callback.answer()
