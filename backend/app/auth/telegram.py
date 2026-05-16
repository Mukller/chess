import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qsl


class InvalidInitDataError(ValueError):
    pass


@dataclass(frozen=True)
class TelegramUser:
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    photo_url: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: dict) -> "TelegramUser":
        return cls(
            id=int(payload["id"]),
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name"),
            username=payload.get("username"),
            language_code=payload.get("language_code"),
            is_premium=bool(payload.get("is_premium", False)),
            photo_url=payload.get("photo_url"),
        )


def _build_data_check_string(pairs: dict) -> str:
    return "\n".join(f"{key}={pairs[key]}" for key in sorted(pairs))


def verify_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 24 * 60 * 60,
) -> TelegramUser:
    """Validates Telegram WebApp initData and returns the authenticated user.

    See https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data:
        raise InvalidInitDataError("empty initData")
    if not bot_token:
        raise InvalidInitDataError("bot token not configured")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=False))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InvalidInitDataError("hash missing in initData")

    data_check_string = _build_data_check_string(pairs)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise InvalidInitDataError("hash mismatch")

    auth_date_raw = pairs.get("auth_date")
    if auth_date_raw is None:
        raise InvalidInitDataError("auth_date missing")
    try:
        auth_date = int(auth_date_raw)
    except ValueError as exc:
        raise InvalidInitDataError("auth_date is not an integer") from exc

    if max_age_seconds > 0 and (time.time() - auth_date) > max_age_seconds:
        raise InvalidInitDataError("initData expired")

    user_raw = pairs.get("user")
    if not user_raw:
        raise InvalidInitDataError("user payload missing")
    try:
        user_dict = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise InvalidInitDataError("user payload is not valid JSON") from exc

    return TelegramUser.from_dict(user_dict)
