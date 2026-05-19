import hashlib

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.auth.jwt_utils import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AnonymousLoginRequest(BaseModel):
    device_id: str = Field(..., min_length=8, max_length=128)


class LoginUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUser


@router.post("/anonymous", response_model=LoginResponse)
async def login_anonymous(payload: AnonymousLoginRequest) -> LoginResponse:
    digest = hashlib.sha256(payload.device_id.encode()).digest()
    user_id = int.from_bytes(digest[:8], "big") % (10**15) + 1
    token = create_access_token(user_id, extra={"name": "Игрок"})
    return LoginResponse(
        access_token=token,
        user=LoginUser(id=user_id, first_name="Игрок"),
    )
