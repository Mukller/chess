import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.jwt_utils import InvalidTokenError, decode_access_token
from app.config import get_settings
from app.storage.redis_client import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window per-user rate limiter backed by Redis sorted sets."""

    EXEMPT_PATHS = {"/health", "/api/auth/telegram", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if request.method == "OPTIONS" or request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        if request.url.path.startswith("/ws/"):
            return await call_next(request)

        identity = self._identity_for(request)
        limit = settings.rate_limit_per_minute
        if identity and limit > 0:
            allowed = await self._check_limit(identity, limit)
            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "rate limit exceeded"},
                )
        return await call_next(request)

    def _identity_for(self, request: Request) -> str | None:
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            try:
                payload = decode_access_token(auth.split(" ", 1)[1].strip())
                return f"user:{payload.get('sub')}"
            except InvalidTokenError:
                pass
        client = request.client
        if client and client.host:
            return f"ip:{client.host}"
        return None

    async def _check_limit(self, identity: str, limit: int) -> bool:
        redis = get_redis()
        key = f"ratelimit:{identity}"
        now_ms = int(time.time() * 1000)
        window_ms = 60_000

        async with redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, now_ms - window_ms)
            pipe.zadd(key, {f"{now_ms}-{id(identity)}": now_ms})
            pipe.zcard(key)
            pipe.pexpire(key, window_ms * 2)
            _, _, count, _ = await pipe.execute()
        return int(count) <= limit
