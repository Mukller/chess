import time
from typing import Optional

import jwt

from app.config import get_settings


class InvalidTokenError(ValueError):
    pass


def create_access_token(user_id: int, *, extra: Optional[dict] = None) -> str:
    settings = get_settings()
    now = int(time.time())
    payload: dict = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.jwt_expires_minutes * 60,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.app_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.app_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise InvalidTokenError("token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError("invalid token") from exc
