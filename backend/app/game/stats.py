import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Optional

from app.game.models import Color, Difficulty, GameStatus
from app.storage.redis_client import get_redis

logger = logging.getLogger(__name__)


INITIAL_ELO = 1200
K_FACTOR = 32

OPPONENT_ELO: dict[Difficulty, int] = {
    Difficulty.EASY: 800,
    Difficulty.MEDIUM: 1400,
    Difficulty.HARD: 1900,
    Difficulty.EXPERT: 2400,
}


@dataclass
class DifficultyStats:
    played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0


@dataclass
class UserStats:
    user_id: int
    elo: int = INITIAL_ELO
    peak_elo: int = INITIAL_ELO
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    by_difficulty: dict[str, DifficultyStats] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["by_difficulty"] = {k: asdict(v) for k, v in self.by_difficulty.items()}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "UserStats":
        by_diff_raw = data.get("by_difficulty", {}) or {}
        by_diff = {k: DifficultyStats(**v) for k, v in by_diff_raw.items()}
        return cls(
            user_id=int(data["user_id"]),
            elo=int(data.get("elo", INITIAL_ELO)),
            peak_elo=int(data.get("peak_elo", data.get("elo", INITIAL_ELO))),
            games_played=int(data.get("games_played", 0)),
            wins=int(data.get("wins", 0)),
            losses=int(data.get("losses", 0)),
            draws=int(data.get("draws", 0)),
            by_difficulty=by_diff,
        )

    @classmethod
    def new(cls, user_id: int) -> "UserStats":
        return cls(user_id=user_id)


@dataclass
class EloUpdate:
    stats: UserStats
    elo_before: int
    elo_after: int
    delta: int


def _expected_score(player_elo: int, opponent_elo: int) -> float:
    return 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))


class StatsService:
    KEY_FMT = "user:{user_id}:stats"
    TTL_SECONDS = 60 * 60 * 24 * 365 * 5

    def __init__(self) -> None:
        self._redis = get_redis()

    def _key(self, user_id: int) -> str:
        return self.KEY_FMT.format(user_id=user_id)

    async def get(self, user_id: int) -> UserStats:
        raw = await self._redis.get(self._key(user_id))
        if raw is None:
            return UserStats.new(user_id)
        try:
            return UserStats.from_dict(json.loads(raw))
        except Exception:
            logger.exception("Failed to parse stats for user %d, resetting", user_id)
            return UserStats.new(user_id)

    async def _save(self, stats: UserStats) -> None:
        await self._redis.set(
            self._key(stats.user_id),
            json.dumps(stats.to_dict()),
            ex=self.TTL_SECONDS,
        )

    async def record_result(
        self,
        user_id: int,
        difficulty: Difficulty,
        user_score: float,
    ) -> EloUpdate:
        """user_score: 1.0 win, 0.5 draw, 0.0 loss."""
        stats = await self.get(user_id)
        elo_before = stats.elo
        opponent_elo = OPPONENT_ELO.get(difficulty, 1400)
        expected = _expected_score(stats.elo, opponent_elo)
        delta = round(K_FACTOR * (user_score - expected))
        new_elo = max(100, stats.elo + delta)

        stats.elo = new_elo
        stats.peak_elo = max(stats.peak_elo, new_elo)
        stats.games_played += 1
        if user_score == 1.0:
            stats.wins += 1
        elif user_score == 0.0:
            stats.losses += 1
        else:
            stats.draws += 1

        diff_key = difficulty.value
        diff_stats = stats.by_difficulty.setdefault(diff_key, DifficultyStats())
        diff_stats.played += 1
        if user_score == 1.0:
            diff_stats.wins += 1
        elif user_score == 0.0:
            diff_stats.losses += 1
        else:
            diff_stats.draws += 1

        await self._save(stats)
        return EloUpdate(stats=stats, elo_before=elo_before, elo_after=new_elo, delta=delta)

    async def reset(self, user_id: int) -> UserStats:
        fresh = UserStats.new(user_id)
        await self._save(fresh)
        return fresh
