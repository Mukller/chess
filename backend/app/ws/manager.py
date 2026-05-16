import asyncio
import json
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Maps game_id -> set of websocket connections for broadcasting state."""

    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, game_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[game_id].add(websocket)

    async def disconnect(self, game_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(game_id)
            if not sockets:
                return
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(game_id, None)

    async def broadcast(self, game_id: str, message: dict) -> None:
        async with self._lock:
            sockets = list(self._connections.get(game_id, ()))
        if not sockets:
            return
        payload = json.dumps(message, separators=(",", ":"))
        dead: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_text(payload)
            except Exception:  # noqa: BLE001
                dead.append(socket)
        if dead:
            async with self._lock:
                live = self._connections.get(game_id)
                if live is not None:
                    for socket in dead:
                        live.discard(socket)
                    if not live:
                        self._connections.pop(game_id, None)


manager = ConnectionManager()
