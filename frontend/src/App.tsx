import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "./api/client";
import { GamePage } from "./pages/GamePage";
import { HomePage } from "./pages/HomePage";
import { useGameStore, useSessionStore } from "./store/gameStore";
import type { Color, Difficulty } from "./types/game";

type View = "loading" | "home" | "game";

function getOrCreateDeviceId(): string {
  const key = "chess_device_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export function App() {
  const session = useSessionStore();
  const game = useGameStore((s) => s.game);
  const setGame = useGameStore((s) => s.setGame);
  const setError = useGameStore((s) => s.setError);
  const errorMessage = useGameStore((s) => s.errorMessage);
  const resetGame = useGameStore((s) => s.reset);

  const [view, setView] = useState<View>("loading");
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      const deviceId = getOrCreateDeviceId();
      try {
        const response = await api.loginAnonymous(deviceId);
        if (cancelled) return;
        session.setSession({ token: response.access_token, user: response.user });
        setView("home");
      } catch (error) {
        if (cancelled) return;
        const message =
          error instanceof ApiError ? error.detail ?? error.message : String(error);
        setError(`Ошибка подключения: ${message}`);
        setView("home");
      }
    }
    bootstrap();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleStart = useCallback(
    async (options: { difficulty: Difficulty; user_color: Color }) => {
      if (!session.token) return;
      setStarting(true);
      setError(null);
      try {
        const state = await api.startGame(session.token, options);
        setGame(state);
        setView("game");
      } catch (error) {
        const message =
          error instanceof ApiError ? error.detail ?? error.message : String(error);
        setError(message);
      } finally {
        setStarting(false);
      }
    },
    [session.token, setError, setGame],
  );

  const handleLeave = useCallback(() => {
    resetGame();
    setView("home");
  }, [resetGame]);

  if (view === "loading") {
    return (
      <div className="flex h-screen items-center justify-center text-surface-hint">
        Подключение…
      </div>
    );
  }

  if (view === "game" && game) {
    return <GamePage onLeave={handleLeave} />;
  }

  return (
    <HomePage
      starting={starting}
      errorMessage={errorMessage}
      onStart={handleStart}
    />
  );
}
