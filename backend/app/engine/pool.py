import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import chess
import chess.engine

from app.config import get_settings
from app.engine.config import profile_for
from app.game.models import Difficulty

logger = logging.getLogger(__name__)


@dataclass
class EngineResult:
    move: Optional[chess.Move]
    score: Optional[float] = None
    mate_in: Optional[int] = None
    depth: Optional[int] = None


class _Worker:
    def __init__(self, worker_id: int, path: str, threads: int, hash_mb: int) -> None:
        self.id = worker_id
        self._path = path
        self._threads = threads
        self._hash_mb = hash_mb
        self._transport: Optional[asyncio.SubprocessTransport] = None
        self._engine: Optional[chess.engine.UciProtocol] = None

    async def start(self) -> None:
        self._transport, self._engine = await chess.engine.popen_uci(self._path)
        await self._engine.configure(
            {
                "Threads": self._threads,
                "Hash": self._hash_mb,
            }
        )
        logger.info("engine worker %d started (path=%s)", self.id, self._path)

    async def best_move(self, board: chess.Board, difficulty: Difficulty) -> EngineResult:
        if self._engine is None:
            raise RuntimeError("worker not started")

        profile = profile_for(difficulty)
        # Skill Level is set per-request so workers can multiplex difficulties.
        await self._engine.configure({"Skill Level": profile.skill_level})

        limit = chess.engine.Limit(
            depth=profile.depth,
            time=max(profile.move_time_ms / 1000.0, 0.05),
        )
        info = await self._engine.play(board, limit, info=chess.engine.INFO_SCORE | chess.engine.INFO_PV)
        score_value: Optional[float] = None
        mate_in: Optional[int] = None
        depth_value: Optional[int] = None
        raw_info = info.info or {}
        if "score" in raw_info:
            relative = raw_info["score"].white()
            mate = relative.mate()
            if mate is not None:
                mate_in = int(mate)
            else:
                cp = relative.score()
                if cp is not None:
                    score_value = round(cp / 100.0, 2)
        if "depth" in raw_info:
            depth_value = int(raw_info["depth"])

        return EngineResult(
            move=info.move,
            score=score_value,
            mate_in=mate_in,
            depth=depth_value,
        )

    async def stop(self) -> None:
        if self._engine is not None:
            try:
                await self._engine.quit()
            except Exception:  # noqa: BLE001
                logger.exception("error stopping worker %d", self.id)
            finally:
                self._engine = None
                self._transport = None


class EnginePool:
    """Async queue dispatching analysis requests across a fixed pool of Stockfish processes."""

    def __init__(
        self,
        path: str,
        size: int,
        *,
        threads: int = 1,
        hash_mb: int = 32,
    ) -> None:
        self._path = path
        self._size = max(1, size)
        self._threads = threads
        self._hash_mb = hash_mb
        self._available: asyncio.Queue[_Worker] = asyncio.Queue()
        self._workers: list[_Worker] = []
        self._started = False
        self._lock = asyncio.Lock()

    @classmethod
    def from_settings(cls) -> "EnginePool":
        settings = get_settings()
        return cls(
            path=settings.stockfish_path,
            size=settings.stockfish_workers,
            threads=settings.stockfish_threads,
            hash_mb=settings.stockfish_hash_mb,
        )

    async def start(self) -> None:
        async with self._lock:
            if self._started:
                return
            for index in range(self._size):
                worker = _Worker(index, self._path, self._threads, self._hash_mb)
                try:
                    await worker.start()
                except FileNotFoundError:
                    logger.error("stockfish binary not found at %s — pool disabled", self._path)
                    await self._shutdown_locked()
                    raise
                self._workers.append(worker)
                await self._available.put(worker)
            self._started = True
            logger.info("engine pool ready with %d workers", len(self._workers))

    async def best_move(
        self,
        board: chess.Board,
        difficulty: Difficulty,
        *,
        allow_ponder: bool = False,  # reserved for future use
    ) -> EngineResult:
        if not self._started:
            await self.start()
        worker = await self._available.get()
        try:
            return await worker.best_move(board, difficulty)
        finally:
            self._available.put_nowait(worker)

    async def shutdown(self) -> None:
        async with self._lock:
            await self._shutdown_locked()

    async def _shutdown_locked(self) -> None:
        for worker in self._workers:
            await worker.stop()
        self._workers.clear()
        while not self._available.empty():
            try:
                self._available.get_nowait()
            except asyncio.QueueEmpty:
                break
        self._started = False
