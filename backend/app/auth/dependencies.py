from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.auth.jwt_utils import InvalidTokenError, decode_access_token


def get_current_user_id(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> int:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token missing subject",
        )
    return int(sub)


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
