import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.game.models import Color, Difficulty, GameStatus
from app.storage.redis_client import get_redis

logger = logging.getLogger(__name__)


TZ_MSK = timezone(timedelta(hours=3))


def now_msk_iso() -> str:
    return datetime.now(TZ_MSK).strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class GameHistoryEntry:
    game_id: str
    user_id: int
    difficulty: str
    user_color: str
    status: str
    result: str  # "win" | "loss" | "draw" | "aborted"
    started_at: str  # ISO format MSK
    finished_at: str  # ISO format MSK
    moves_uci: List[str] = field(default_factory=list)
    final_fen: str = ""
    elo_before: int = 0
    elo_after: int = 0
    elo_delta: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameHistoryEntry":
        return cls(
            game_id=data["game_id"],
            user_id=int(data["user_id"]),
            difficulty=data.get("difficulty", "medium"),
            user_color=data.get("user_color", "white"),
            status=data.get("status", "unknown"),
            result=data.get("result", "unknown"),
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
            moves_uci=list(data.get("moves_uci", [])),
            final_fen=data.get("final_fen", ""),
            elo_before=int(data.get("elo_before", 0)),
            elo_after=int(data.get("elo_after", 0)),
            elo_delta=int(data.get("elo_delta", 0)),
        )


class HistoryService:
    """Persists finished games for replay/review. Stored in Redis without short TTL."""

    INDEX_KEY = "user:{user_id}:history"
    ENTRY_KEY = "game_history:{game_id}"
    TTL_SECONDS = 60 * 60 * 24 * 365 * 5  # 5 years
    MAX_ENTRIES_PER_USER = 200

    def __init__(self) -> None:
        self._redis = get_redis()

    def _index_key(self, user_id: int) -> str:
        return self.INDEX_KEY.format(user_id=user_id)

    def _entry_key(self, game_id: str) -> str:
        return self.ENTRY_KEY.format(game_id=game_id)

    async def save(self, entry: GameHistoryEntry) -> None:
        try:
            payload = json.dumps(entry.to_dict(), separators=(",", ":"), ensure_ascii=False)
            score = int(datetime.now(TZ_MSK).timestamp())
            async with self._redis.pipeline(transaction=True) as pipe:
                pipe.set(self._entry_key(entry.game_id), payload, ex=self.TTL_SECONDS)
                pipe.zadd(self._index_key(entry.user_id), {entry.game_id: score})
                pipe.expire(self._index_key(entry.user_id), self.TTL_SECONDS)
                # Trim old entries beyond MAX
                pipe.zremrangebyrank(self._index_key(entry.user_id), 0, -(self.MAX_ENTRIES_PER_USER + 1))
                await pipe.execute()
        except Exception:
            logger.exception("Failed to save game history for user %d", entry.user_id)

    async def list_recent(self, user_id: int, limit: int = 10, offset: int = 0) -> List[GameHistoryEntry]:
        try:
            ids = await self._redis.zrevrange(
                self._index_key(user_id), offset, offset + max(0, limit - 1)
            )
            if not ids:
                return []
            keys = [self._entry_key(gid) for gid in ids]
            raws = await self._redis.mget(*keys)
            entries: List[GameHistoryEntry] = []
            for raw in raws:
                if not raw:
                    continue
                try:
                    entries.append(GameHistoryEntry.from_dict(json.loads(raw)))
                except Exception:
                    logger.exception("Skipping corrupt history entry")
            return entries
        except Exception:
            logger.exception("Failed to list history for user %d", user_id)
            return []

    async def count(self, user_id: int) -> int:
        try:
            return int(await self._redis.zcard(self._index_key(user_id)) or 0)
        except Exception:
            return 0

    async def get(self, game_id: str, user_id: int) -> Optional[GameHistoryEntry]:
        try:
            raw = await self._redis.get(self._entry_key(game_id))
            if not raw:
                return None
            entry = GameHistoryEntry.from_dict(json.loads(raw))
            if entry.user_id != user_id:
                return None
            return entry
        except Exception:
            logger.exception("Failed to get history entry %s", game_id)
            return None
