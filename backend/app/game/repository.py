import json
from typing import List, Optional

from app.config import get_settings
from app.game.models import GameState
from app.storage.redis_client import get_redis

DEFAULT_RATING = 1200


def _game_key(game_id: str) -> str:
    return f"game:{game_id}"


def _user_index_key(user_id: int) -> str:
    return f"user:{user_id}:games"


def _rating_key(user_id: int) -> str:
    return f"rating:{user_id}"


class GameRepository:
    """Persistence layer for active games (Redis-backed per spec)."""

    async def save(self, state: GameState) -> None:
        settings = get_settings()
        redis = get_redis()
        state.touch()
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        async with redis.pipeline(transaction=True) as pipe:
            pipe.set(_game_key(state.game_id), payload, ex=settings.redis_game_ttl_seconds)
            pipe.zadd(_user_index_key(state.user_id), {state.game_id: state.updated_at})
            pipe.expire(_user_index_key(state.user_id), settings.redis_game_ttl_seconds)
            await pipe.execute()

    async def get(self, game_id: str) -> Optional[GameState]:
        redis = get_redis()
        raw = await redis.get(_game_key(game_id))
        if raw is None:
            return None
        return GameState.from_dict(json.loads(raw))

    async def delete(self, game_id: str, user_id: int) -> None:
        redis = get_redis()
        async with redis.pipeline(transaction=True) as pipe:
            pipe.delete(_game_key(game_id))
            pipe.zrem(_user_index_key(user_id), game_id)
            await pipe.execute()

    async def list_for_user(self, user_id: int, limit: int = 20) -> List[str]:
        redis = get_redis()
        return await redis.zrevrange(_user_index_key(user_id), 0, max(0, limit - 1))

    async def get_rating(self, user_id: int) -> int:
        redis = get_redis()
        val = await redis.get(_rating_key(user_id))
        return int(val) if val else DEFAULT_RATING

    async def save_rating(self, user_id: int, rating: int) -> None:
        redis = get_redis()
        await redis.set(_rating_key(user_id), str(rating))
