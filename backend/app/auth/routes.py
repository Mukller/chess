from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.jwt_utils import create_access_token
from app.auth.telegram import InvalidInitDataError, TelegramUser, verify_init_data
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    init_data: str = Field(..., description="Raw Telegram WebApp initData query string")


class LoginUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUser


@router.post("/telegram", response_model=LoginResponse)
async def login_telegram(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    try:
        user: TelegramUser = verify_init_data(
            payload.init_data,
            settings.telegram_bot_token,
            max_age_seconds=settings.jwt_expires_minutes * 60,
        )
    except InvalidInitDataError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token = create_access_token(
        user.id,
        extra={"name": user.first_name, "username": user.username or ""},
    )
    return LoginResponse(
        access_token=token,
        user=LoginUser(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            photo_url=user.photo_url,
        ),
    )
