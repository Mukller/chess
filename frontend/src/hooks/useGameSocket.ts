import { useEffect, useRef } from "react";

import { GameSocket } from "../api/websocket";
import { useGameStore } from "../store/gameStore";

export function useGameSocket(token: string | null, gameId: string | null) {
  const socketRef = useRef<GameSocket | null>(null);
  const setGame = useGameStore((s) => s.setGame);
  const setConnected = useGameStore((s) => s.setConnected);
  const setError = useGameStore((s) => s.setError);
  const setThinking = useGameStore((s) => s.setThinking);
  const applyEngineSan = useGameStore((s) => s.applyEngineSan);

  useEffect(() => {
    if (!token || !gameId) return;
    const socket = new GameSocket(gameId, token, {
      onEvent: (event) => {
        switch (event.type) {
          case "snapshot":
          case "position": {
            setGame(event.state);
            if ("engine_move" in event) {
              applyEngineSan(event.engine_move?.san ?? null);
            }
            setThinking(false);
            break;
          }
          case "game_over": {
            setError(`Игра окончена: ${event.status}${event.result ? ` (${event.result})` : ""}`);
            setThinking(false);
            break;
          }
          case "error": {
            setError(event.detail);
            setThinking(false);
            break;
          }
          case "pong":
            break;
        }
      },
      onOpen: () => {
        setConnected(true);
        setError(null);
      },
      onClose: () => {
        setConnected(false);
      },
    });
    socket.connect();
    socketRef.current = socket;
    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [token, gameId, setGame, setConnected, setError, setThinking, applyEngineSan]);

  return socketRef;
}
