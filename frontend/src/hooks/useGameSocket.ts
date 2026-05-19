import { useEffect, useRef } from "react";

import { GameSocket } from "../api/websocket";
import { useGameStore, useSessionStore } from "../store/gameStore";
import type { GameStatus } from "../types/game";

export function useGameSocket(token: string | null, gameId: string | null) {
  const socketRef = useRef<GameSocket | null>(null);
  const setGame = useGameStore((s) => s.setGame);
  const setConnected = useGameStore((s) => s.setConnected);
  const setError = useGameStore((s) => s.setError);
  const setThinking = useGameStore((s) => s.setThinking);
  const applyEngineSan = useGameStore((s) => s.applyEngineSan);
  const setRatingChange = useGameStore((s) => s.setRatingChange);
  const setRating = useSessionStore((s) => s.setRating);

  useEffect(() => {
    if (!token || !gameId) return;
    const socket = new GameSocket(gameId, token, {
      onEvent: (event) => {
        switch (event.type) {
          case "snapshot": {
            setGame(event.state);
            setRating(event.rating);
            setThinking(false);
            break;
          }
          case "position": {
            setGame(event.state);
            if ("engine_move" in event) {
              applyEngineSan(event.engine_move?.san ?? null);
            }
            setThinking(false);
            break;
          }
          case "game_over": {
            // Update game state status — essential for resign (no position event precedes it)
            const currentGame = useGameStore.getState().game;
            if (currentGame) {
              setGame({
                ...currentGame,
                status: event.status as GameStatus,
                result: event.result,
              });
            }
            setRating(event.rating);
            setRatingChange(event.rating_change);
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
  }, [token, gameId, setGame, setConnected, setError, setThinking, applyEngineSan, setRating, setRatingChange]);

  return socketRef;
}
