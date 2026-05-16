import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

import chess

from app.game.models import Color, Difficulty, GameState, GameStatus
from app.game.repository import GameRepository

if TYPE_CHECKING:
    from app.engine.pool import EnginePool, EngineResult

logger = logging.getLogger(__name__)


class GameError(Exception):
    """Base error for game service failures."""


class GameNotFoundError(GameError):
    pass


class GameForbiddenError(GameError):
    pass


class IllegalMoveError(GameError):
    pass


class GameAlreadyFinishedError(GameError):
    pass


@dataclass
class MoveOutcome:
    state: GameState
    player_move_uci: str
    engine_move_uci: Optional[str]
    engine_move_san: Optional[str]


class GameService:
    """Authoritative chess game logic per spec — backend always validates."""

    def __init__(self, repository: Optional[GameRepository] = None) -> None:
        self.repository = repository or GameRepository()

    async def start(
        self,
        user_id: int,
        *,
        difficulty: Difficulty,
        user_color: Color,
        engine_pool: Optional["EnginePool"] = None,
    ) -> GameState:
        board = chess.Board()
        state = GameState.new(
            user_id=user_id,
            starting_fen=board.fen(),
            difficulty=difficulty,
            user_color=user_color,
        )

        if user_color is Color.BLACK and engine_pool is not None:
            result = await engine_pool.best_move(board, difficulty)
            if result.move is not None:
                board.push(result.move)
                state.fen = board.fen()
                state.moves.append(result.move.uci())
                state.last_engine_move = result.move.uci()

        await self.repository.save(state)
        return state

    async def get(self, game_id: str, user_id: int) -> GameState:
        state = await self.repository.get(game_id)
        if state is None:
            raise GameNotFoundError(f"game {game_id} not found")
        if state.user_id != user_id:
            raise GameForbiddenError("game belongs to another user")
        return state

    async def make_move(
        self,
        game_id: str,
        user_id: int,
        move_uci: str,
        *,
        engine_pool: Optional["EnginePool"] = None,
    ) -> MoveOutcome:
        state = await self.get(game_id, user_id)
        if state.status is not GameStatus.ACTIVE:
            raise GameAlreadyFinishedError(f"game already {state.status.value}")

        board = chess.Board(state.fen)
        expected_turn = chess.WHITE if state.user_color is Color.WHITE else chess.BLACK
        if board.turn != expected_turn:
            raise IllegalMoveError("not your turn")

        try:
            player_move = chess.Move.from_uci(move_uci)
        except (chess.InvalidMoveError, ValueError) as exc:
            raise IllegalMoveError(f"invalid move format: {move_uci}") from exc

        if player_move not in board.legal_moves:
            raise IllegalMoveError(f"illegal move: {move_uci}")

        board.push(player_move)
        state.moves.append(player_move.uci())
        state.fen = board.fen()
        state.last_engine_move = None

        engine_move_uci: Optional[str] = None
        engine_move_san: Optional[str] = None

        if self._update_terminal_status(board, state):
            await self.repository.save(state)
            return MoveOutcome(
                state=state,
                player_move_uci=player_move.uci(),
                engine_move_uci=None,
                engine_move_san=None,
            )

        if engine_pool is not None:
            engine_result: "EngineResult" = await engine_pool.best_move(board, state.difficulty)
            if engine_result.move is not None:
                engine_move_san = board.san(engine_result.move)
                board.push(engine_result.move)
                state.moves.append(engine_result.move.uci())
                state.fen = board.fen()
                state.last_engine_move = engine_result.move.uci()
                engine_move_uci = engine_result.move.uci()
                self._update_terminal_status(board, state)

        await self.repository.save(state)
        return MoveOutcome(
            state=state,
            player_move_uci=player_move.uci(),
            engine_move_uci=engine_move_uci,
            engine_move_san=engine_move_san,
        )

    async def undo(
        self,
        game_id: str,
        user_id: int,
    ) -> GameState:
        state = await self.get(game_id, user_id)
        if state.status is not GameStatus.ACTIVE:
            raise GameAlreadyFinishedError("cannot undo on finished game")

        board = chess.Board()
        # Trim to the last position where the user is to move (drop both player + engine).
        history = list(state.moves)
        user_turn_white = state.user_color is Color.WHITE
        trimmed: List[str] = []
        for move in history:
            trimmed.append(move)
            board.push(chess.Move.from_uci(move))

        # Pop pairs (engine + player) until it's user's turn again, or until empty.
        while trimmed:
            top = trimmed[-1]
            board.pop()
            popped = trimmed.pop()
            if board.turn == (chess.WHITE if user_turn_white else chess.BLACK):
                break

        state.moves = trimmed
        state.fen = board.fen()
        state.last_engine_move = trimmed[-1] if trimmed else None
        state.status = GameStatus.ACTIVE
        state.result = None
        await self.repository.save(state)
        return state

    async def resign(self, game_id: str, user_id: int) -> GameState:
        state = await self.get(game_id, user_id)
        if state.status is not GameStatus.ACTIVE:
            return state
        state.status = GameStatus.RESIGNED
        state.result = "0-1" if state.user_color is Color.WHITE else "1-0"
        await self.repository.save(state)
        return state

    async def hint(
        self,
        game_id: str,
        user_id: int,
        *,
        engine_pool: "EnginePool",
    ) -> "EngineResult":
        state = await self.get(game_id, user_id)
        if state.status is not GameStatus.ACTIVE:
            raise GameAlreadyFinishedError("no hint available on finished game")
        board = chess.Board(state.fen)
        return await engine_pool.best_move(board, state.difficulty, allow_ponder=False)

    def derive_board(self, state: GameState) -> chess.Board:
        return chess.Board(state.fen)

    def legal_moves(self, board: chess.Board) -> List[str]:
        return [move.uci() for move in board.legal_moves]

    @staticmethod
    def _update_terminal_status(board: chess.Board, state: GameState) -> bool:
        outcome = board.outcome(claim_draw=True)
        if outcome is None:
            return False
        state.result = outcome.result()
        if outcome.termination is chess.Termination.CHECKMATE:
            state.status = GameStatus.CHECKMATE
        elif outcome.termination is chess.Termination.STALEMATE:
            state.status = GameStatus.STALEMATE
        else:
            state.status = GameStatus.DRAW
        return True


def state_summary(state: GameState, board: Optional[chess.Board] = None) -> Tuple[chess.Board, dict]:
    """Helper for serialising a state alongside derived board info."""
    if board is None:
        board = chess.Board(state.fen)
    turn = Color.WHITE if board.turn == chess.WHITE else Color.BLACK
    return board, {
        "game_id": state.game_id,
        "fen": state.fen,
        "moves": state.moves,
        "difficulty": state.difficulty,
        "user_color": state.user_color,
        "status": state.status,
        "result": state.result,
        "last_engine_move": state.last_engine_move,
        "turn": turn,
        "is_check": board.is_check(),
        "legal_moves": [move.uci() for move in board.legal_moves],
        "created_at": state.created_at,
        "updated_at": state.updated_at,
    }
