import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import List, Optional


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Color(StrEnum):
    WHITE = "white"
    BLACK = "black"


class GameStatus(StrEnum):
    ACTIVE = "active"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"
    ABANDONED = "abandoned"


@dataclass
class GameState:
    game_id: str
    user_id: int
    fen: str
    moves: List[str] = field(default_factory=list)
    difficulty: Difficulty = Difficulty.MEDIUM
    user_color: Color = Color.WHITE
    status: GameStatus = GameStatus.ACTIVE
    result: Optional[str] = None
    created_at: int = field(default_factory=lambda: int(time.time()))
    updated_at: int = field(default_factory=lambda: int(time.time()))
    last_engine_move: Optional[str] = None

    @classmethod
    def new(
        cls,
        user_id: int,
        *,
        starting_fen: str,
        difficulty: Difficulty,
        user_color: Color,
    ) -> "GameState":
        return cls(
            game_id=str(uuid.uuid4()),
            user_id=user_id,
            fen=starting_fen,
            difficulty=difficulty,
            user_color=user_color,
        )

    def touch(self) -> None:
        self.updated_at = int(time.time())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["difficulty"] = self.difficulty.value
        data["user_color"] = self.user_color.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        return cls(
            game_id=data["game_id"],
            user_id=int(data["user_id"]),
            fen=data["fen"],
            moves=list(data.get("moves", [])),
            difficulty=Difficulty(data.get("difficulty", Difficulty.MEDIUM.value)),
            user_color=Color(data.get("user_color", Color.WHITE.value)),
            status=GameStatus(data.get("status", GameStatus.ACTIVE.value)),
            result=data.get("result"),
            created_at=int(data.get("created_at", time.time())),
            updated_at=int(data.get("updated_at", time.time())),
            last_engine_move=data.get("last_engine_move"),
        )
