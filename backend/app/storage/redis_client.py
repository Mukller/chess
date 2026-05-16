from typing import Optional

import redis.asyncio as aioredis

from app.config import get_settings


class RedisClient:
    _instance: Optional["RedisClient"] = None

    def __init__(self) -> None:
        settings = get_settings()
        self._client: aioredis.Redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )

    @classmethod
    def instance(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def client(self) -> aioredis.Redis:
        return self._client

    async def ping(self) -> bool:
        return await self._client.ping()

    async def close(self) -> None:
        await self._client.aclose()


def get_redis() -> aioredis.Redis:
    return RedisClient.instance().client
