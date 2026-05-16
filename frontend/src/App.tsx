import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "./api/client";
import { GamePage } from "./pages/GamePage";
import { HomePage } from "./pages/HomePage";
import { applyTelegramTheme, useTelegram } from "./hooks/useTelegram";
import { useGameStore, useSessionStore } from "./store/gameStore";
import type { Color, Difficulty } from "./types/game";

type View = "loading" | "home" | "game" | "error";

export function App() {
  const tg = useTelegram();
  const session = useSessionStore();
  const game = useGameStore((s) => s.game);
  const setGame = useGameStore((s) => s.setGame);
  const setError = useGameStore((s) => s.setError);
  const errorMessage = useGameStore((s) => s.errorMessage);
  const resetGame = useGameStore((s) => s.reset);

  const [view, setView] = useState<View>("loading");
  const [bootError, setBootError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    applyTelegramTheme(tg);
  }, [tg]);

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      const initData = tg?.initData;
      if (!initData) {
        if (!cancelled) {
          setBootError(
            "Telegram WebApp недоступен. Откройте бот в Telegram и нажмите кнопку Играть.",
          );
          setView("error");
        }
        return;
      }
      try {
        const response = await api.loginTelegram(initData);
        if (cancelled) return;
        session.setSession({ token: response.access_token, user: response.user });
        setView("home");
      } catch (error) {
        if (cancelled) return;
        const message =
          error instanceof ApiError ? error.detail ?? error.message : String(error);
        setBootError(`Ошибка авторизации: ${message}`);
        setView("error");
      }
    }
    if (tg) bootstrap();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tg]);

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
        Загружаем Telegram WebApp…
      </div>
    );
  }

  if (view === "error") {
    return (
      <div className="mx-auto flex h-screen max-w-md items-center justify-center p-6 text-center text-sm text-red-600">
        {bootError}
      </div>
    );
  }

  if (view === "game" && game) {
    return <GamePage onLeave={handleLeave} />;
  }

  return (
    <HomePage
      userName={session.user?.first_name ?? "игрок"}
      starting={starting}
      errorMessage={errorMessage}
      onStart={handleStart}
    />
  );
}
