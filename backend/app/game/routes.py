from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import CurrentUserId
from app.game.schemas import (
    EngineMoveSummary,
    GameStateResponse,
    HintResponse,
    MoveRequest,
    MoveResponse,
    StartGameRequest,
)
from app.game.service import (
    GameAlreadyFinishedError,
    GameForbiddenError,
    GameNotFoundError,
    GameService,
    IllegalMoveError,
    state_summary,
)

router = APIRouter(prefix="/api/game", tags=["game"])


def get_service() -> GameService:
    return GameService()


def get_engine_pool(request: Request):
    return getattr(request.app.state, "engine_pool", None)


ServiceDep = Annotated[GameService, Depends(get_service)]


def _state_response(state) -> GameStateResponse:
    _, summary = state_summary(state)
    return GameStateResponse(**summary)


def _engine_pool_or_503(pool):
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="chess engine not ready",
        )
    return pool


@router.post("/start", response_model=GameStateResponse, status_code=status.HTTP_201_CREATED)
async def start_game(
    payload: StartGameRequest,
    user_id: CurrentUserId,
    service: ServiceDep,
    request: Request,
) -> GameStateResponse:
    pool = get_engine_pool(request)
    state = await service.start(
        user_id,
        difficulty=payload.difficulty,
        user_color=payload.user_color,
        engine_pool=pool,
    )
    return _state_response(state)


@router.get("/{game_id}", response_model=GameStateResponse)
async def get_game(
    game_id: str,
    user_id: CurrentUserId,
    service: ServiceDep,
) -> GameStateResponse:
    try:
        state = await service.get(game_id, user_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GameForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return _state_response(state)


@router.post("/{game_id}/move", response_model=MoveResponse)
async def make_move(
    game_id: str,
    payload: MoveRequest,
    user_id: CurrentUserId,
    service: ServiceDep,
    request: Request,
) -> MoveResponse:
    pool = _engine_pool_or_503(get_engine_pool(request))
    try:
        outcome = await service.make_move(
            game_id,
            user_id,
            payload.move,
            engine_pool=pool,
        )
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GameForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except IllegalMoveError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except GameAlreadyFinishedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    engine_summary = (
        EngineMoveSummary(uci=outcome.engine_move_uci, san=outcome.engine_move_san)
        if outcome.engine_move_uci
        else None
    )
    return MoveResponse(
        state=_state_response(outcome.state),
        player_move=outcome.player_move_uci,
        engine_move=engine_summary,
    )


@router.post("/{game_id}/hint", response_model=HintResponse)
async def get_hint(
    game_id: str,
    user_id: CurrentUserId,
    service: ServiceDep,
    request: Request,
) -> HintResponse:
    pool = _engine_pool_or_503(get_engine_pool(request))
    try:
        result = await service.hint(game_id, user_id, engine_pool=pool)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GameForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except GameAlreadyFinishedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if result.move is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="no legal move available",
        )

    return HintResponse(
        best_move=result.move.uci(),
        evaluation=result.score,
        mate_in=result.mate_in,
        depth=result.depth,
    )


@router.post("/{game_id}/undo", response_model=GameStateResponse)
async def undo_move(
    game_id: str,
    user_id: CurrentUserId,
    service: ServiceDep,
) -> GameStateResponse:
    try:
        state = await service.undo(game_id, user_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GameForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except GameAlreadyFinishedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _state_response(state)


@router.post("/{game_id}/resign", response_model=GameStateResponse)
async def resign_game(
    game_id: str,
    user_id: CurrentUserId,
    service: ServiceDep,
) -> GameStateResponse:
    try:
        state = await service.resign(game_id, user_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GameForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return _state_response(state)
