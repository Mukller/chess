import logging
from typing import Optional

from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect, status

from app.auth.jwt_utils import InvalidTokenError, decode_access_token
from app.game.models import GameStatus
from app.game.service import (
    GameAlreadyFinishedError,
    GameForbiddenError,
    GameNotFoundError,
    GameService,
    IllegalMoveError,
    state_summary,
)
from app.ws.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()

PROTOCOL_VERSION = 1


def _authenticate(token: Optional[str]) -> Optional[int]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        return int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        return None


def _state_payload(state, board=None) -> dict:
    _, summary = state_summary(state, board)
    summary["difficulty"] = summary["difficulty"].value
    summary["user_color"] = summary["user_color"].value
    summary["status"] = summary["status"].value
    summary["turn"] = summary["turn"].value
    return summary


@router.websocket("/ws/game/{game_id}")
async def game_socket(
    websocket: WebSocket,
    game_id: str,
    token: Optional[str] = Query(default=None),
) -> None:
    user_id = _authenticate(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    service = GameService()
    try:
        state = await service.get(game_id, user_id)
    except GameNotFoundError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except GameForbiddenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(game_id, websocket)
    try:
        await websocket.send_json(
            {
                "type": "snapshot",
                "protocol": PROTOCOL_VERSION,
                "state": _state_payload(state),
            }
        )

        engine_pool = getattr(websocket.app.state, "engine_pool", None)

        while True:
            message = await websocket.receive_json()
            kind = message.get("type")

            if kind == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if kind == "move":
                move_uci = message.get("move")
                if not move_uci:
                    await websocket.send_json({"type": "error", "detail": "move missing"})
                    continue
                if engine_pool is None:
                    await websocket.send_json({"type": "error", "detail": "engine unavailable"})
                    continue
                try:
                    outcome = await service.make_move(
                        game_id,
                        user_id,
                        move_uci,
                        engine_pool=engine_pool,
                    )
                except IllegalMoveError as exc:
                    await websocket.send_json({"type": "error", "detail": str(exc)})
                    continue
                except GameAlreadyFinishedError as exc:
                    await websocket.send_json({"type": "error", "detail": str(exc)})
                    continue

                payload = {
                    "type": "position",
                    "state": _state_payload(outcome.state),
                    "player_move": outcome.player_move_uci,
                    "engine_move": (
                        {"uci": outcome.engine_move_uci, "san": outcome.engine_move_san}
                        if outcome.engine_move_uci
                        else None
                    ),
                }
                await manager.broadcast(game_id, payload)

                if outcome.state.status is not GameStatus.ACTIVE:
                    await manager.broadcast(
                        game_id,
                        {
                            "type": "game_over",
                            "result": outcome.state.result,
                            "status": outcome.state.status.value,
                        },
                    )
                continue

            if kind == "resign":
                state = await service.resign(game_id, user_id)
                await manager.broadcast(
                    game_id,
                    {
                        "type": "game_over",
                        "result": state.result,
                        "status": state.status.value,
                    },
                )
                continue

            await websocket.send_json({"type": "error", "detail": f"unknown message type: {kind}"})
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        logger.exception("websocket session crashed (game_id=%s)", game_id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:  # noqa: BLE001
            pass
    finally:
        await manager.disconnect(game_id, websocket)
