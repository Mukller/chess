from typing import List, Optional

from pydantic import BaseModel, Field

from app.game.models import Color, Difficulty, GameStatus


class StartGameRequest(BaseModel):
    difficulty: Difficulty = Difficulty.MEDIUM
    user_color: Color = Color.WHITE


class MoveRequest(BaseModel):
    move: str = Field(
        ...,
        description="UCI move like e2e4 or promotion e7e8q",
        min_length=4,
        max_length=5,
    )


class HintResponse(BaseModel):
    best_move: str
    evaluation: Optional[float] = None
    mate_in: Optional[int] = None
    depth: Optional[int] = None


class EngineMoveSummary(BaseModel):
    uci: str
    san: Optional[str] = None


class GameStateResponse(BaseModel):
    game_id: str
    fen: str
    moves: List[str]
    difficulty: Difficulty
    user_color: Color
    status: GameStatus
    result: Optional[str] = None
    last_engine_move: Optional[str] = None
    turn: Color
    is_check: bool
    legal_moves: List[str]
    created_at: int
    updated_at: int


class MoveResponse(BaseModel):
    state: GameStateResponse
    player_move: str
    engine_move: Optional[EngineMoveSummary] = None
