"""Online PvP: invite codes, two-player game state, Redis pub/sub for live moves.

Status: scaffolding. The bot exposes the menu and creates / joins games via codes.
Live notifications and move synchronization between two clients are wired
through Redis pub/sub channels keyed by game id.
"""
import json
import logging
import random
import string
import time
from dataclasses import asdict, dataclass, field
from typing import Optional

import chess

from app.game.models import Color, GameStatus
from app.storage.redis_client import get_redis

logger = logging.getLogger(__name__)

INVITE_CODE_ALPHABET = string.ascii_uppercase + string.digits
INVITE_CODE_LENGTH = 6


def generate_invite_code() -> str:
    return "".join(random.choices(INVITE_CODE_ALPHABET, k=INVITE_CODE_LENGTH))


@dataclass
class OnlineGame:
    code: str
    game_id: str
    host_user_id: int
    host_username: str
    host_color: str  # "white" | "black"
    guest_user_id: Optional[int] = None
    guest_username: str = ""
    fen: str = chess.STARTING_FEN
    moves: list[str] = field(default_factory=list)
    status: str = "waiting"  # waiting | active | checkmate | stalemate | draw | aborted
    turn: str = "white"
    started_at: int = field(default_factory=lambda: int(time.time()))
    last_activity: int = field(default_factory=lambda: int(time.time()))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OnlineGame":
        return cls(
            code=data["code"],
            game_id=data["game_id"],
            host_user_id=int(data["host_user_id"]),
            host_username=data.get("host_username", ""),
            host_color=data.get("host_color", "white"),
            guest_user_id=int(data["guest_user_id"]) if data.get("guest_user_id") else None,
            guest_username=data.get("guest_username", ""),
            fen=data.get("fen", chess.STARTING_FEN),
            moves=list(data.get("moves", [])),
            status=data.get("status", "waiting"),
            turn=data.get("turn", "white"),
            started_at=int(data.get("started_at", time.time())),
            last_activity=int(data.get("last_activity", time.time())),
        )

    def color_for_user(self, user_id: int) -> Optional[Color]:
        if user_id == self.host_user_id:
            return Color(self.host_color)
        if self.guest_user_id and user_id == self.guest_user_id:
            return Color.WHITE if self.host_color == "black" else Color.BLACK
        return None

    def opponent_user_id(self, user_id: int) -> Optional[int]:
        if user_id == self.host_user_id:
            return self.guest_user_id
        if user_id == self.guest_user_id:
            return self.host_user_id
        return None


class OnlineService:
    CODE_KEY = "online:code:{code}"
    GAME_KEY = "online:game:{game_id}"
    CHANNEL = "online:notify:{user_id}"
    TTL_SECONDS = 60 * 60 * 24  # 24h

    def __init__(self) -> None:
        self._redis = get_redis()

    async def create(self, host_user_id: int, host_username: str, host_color: Color) -> OnlineGame:
        code = generate_invite_code()
        # avoid collisions
        for _ in range(5):
            exists = await self._redis.exists(self.CODE_KEY.format(code=code))
            if not exists:
                break
            code = generate_invite_code()

        game = OnlineGame(
            code=code,
            game_id=f"pvp-{code}-{int(time.time())}",
            host_user_id=host_user_id,
            host_username=host_username,
            host_color=host_color.value,
        )
        await self._save(game)
        await self._redis.set(self.CODE_KEY.format(code=code), game.game_id, ex=self.TTL_SECONDS)
        return game

    async def join(self, code: str, guest_user_id: int, guest_username: str) -> Optional[OnlineGame]:
        gid_raw = await self._redis.get(self.CODE_KEY.format(code=code.upper()))
        if not gid_raw:
            return None
        game = await self._get_by_game_id(gid_raw)
        if game is None:
            return None
        if game.guest_user_id and game.guest_user_id != guest_user_id:
            return None
        if game.host_user_id == guest_user_id:
            return None
        game.guest_user_id = guest_user_id
        game.guest_username = guest_username
        game.status = "active"
        game.last_activity = int(time.time())
        await self._save(game)
        await self._notify(game.host_user_id, {"type": "joined", "code": game.code, "game_id": game.game_id})
        return game

    async def get(self, game_id: str) -> Optional[OnlineGame]:
        return await self._get_by_game_id(game_id)

    async def _get_by_game_id(self, game_id: str) -> Optional[OnlineGame]:
        raw = await self._redis.get(self.GAME_KEY.format(game_id=game_id))
        if not raw:
            return None
        try:
            return OnlineGame.from_dict(json.loads(raw))
        except Exception:
            logger.exception("Failed to parse online game %s", game_id)
            return None

    async def _save(self, game: OnlineGame) -> None:
        game.last_activity = int(time.time())
        await self._redis.set(
            self.GAME_KEY.format(game_id=game.game_id),
            json.dumps(game.to_dict(), separators=(",", ":")),
            ex=self.TTL_SECONDS,
        )

    async def apply_move(self, game_id: str, user_id: int, move_uci: str) -> tuple[Optional[OnlineGame], str]:
        """Returns (game, error). On success error == ''."""
        game = await self._get_by_game_id(game_id)
        if not game:
            return None, "Игра не найдена"
        if game.status != "active":
            return game, "Игра не активна"
        user_color = game.color_for_user(user_id)
        if not user_color:
            return game, "Вы не участник этой игры"
        if game.turn != user_color.value:
            return game, "Сейчас не ваш ход"
        board = chess.Board(game.fen)
        try:
            move = chess.Move.from_uci(move_uci)
        except Exception:
            return game, "Некорректный формат хода"
        if move not in board.legal_moves:
            return game, "Нелегальный ход"
        board.push(move)
        game.moves.append(move.uci())
        game.fen = board.fen()
        game.turn = "white" if board.turn == chess.WHITE else "black"

        if board.is_checkmate():
            game.status = "checkmate"
        elif board.is_stalemate():
            game.status = "stalemate"
        elif board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            game.status = "draw"

        await self._save(game)
        opp_id = game.opponent_user_id(user_id)
        if opp_id:
            await self._notify(opp_id, {
                "type": "move",
                "game_id": game.game_id,
                "move": move_uci,
                "fen": game.fen,
                "turn": game.turn,
                "status": game.status,
            })
        return game, ""

    async def abort(self, game_id: str, user_id: int) -> Optional[OnlineGame]:
        game = await self._get_by_game_id(game_id)
        if not game:
            return None
        if user_id not in (game.host_user_id, game.guest_user_id):
            return game
        game.status = "aborted"
        await self._save(game)
        opp_id = game.opponent_user_id(user_id)
        if opp_id:
            await self._notify(opp_id, {"type": "aborted", "game_id": game.game_id})
        return game

    async def _notify(self, user_id: int, payload: dict) -> None:
        try:
            await self._redis.publish(
                self.CHANNEL.format(user_id=user_id),
                json.dumps(payload, separators=(",", ":")),
            )
        except Exception:
            logger.exception("Failed to publish notification for user %d", user_id)
