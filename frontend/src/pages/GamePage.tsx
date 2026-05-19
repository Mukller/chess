import { useCallback, useState } from "react";

import { Board } from "../components/Board";
import { GameControls } from "../components/GameControls";
import { HintPanel } from "../components/HintPanel";
import { MoveList } from "../components/MoveList";
import { useGameSocket } from "../hooks/useGameSocket";
import { api, ApiError } from "../api/client";
import { useGameStore, useSessionStore } from "../store/gameStore";

interface Props {
  onLeave: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  active: "Идёт партия",
  checkmate: "Мат",
  stalemate: "Пат",
  draw: "Ничья",
  resigned: "Сдача",
  abandoned: "Партия покинута",
};

const RESULT_LABEL: Record<string, string> = {
  checkmate: "Мат — партия завершена",
  stalemate: "Пат — ничья",
  draw: "Ничья",
  resigned: "Вы сдались",
  abandoned: "Партия покинута",
};

export function GamePage({ onLeave }: Props) {
  const token = useSessionStore((s) => s.token);
  const rating = useSessionStore((s) => s.rating);
  const game = useGameStore((s) => s.game);
  const hint = useGameStore((s) => s.hint);
  const isThinking = useGameStore((s) => s.isThinking);
  const setThinking = useGameStore((s) => s.setThinking);
  const setHint = useGameStore((s) => s.setHint);
  const setError = useGameStore((s) => s.setError);
  const setGame = useGameStore((s) => s.setGame);
  const errorMessage = useGameStore((s) => s.errorMessage);
  const connected = useGameStore((s) => s.socketConnected);
  const lastEngineSan = useGameStore((s) => s.lastEngineSan);
  const ratingChange = useGameStore((s) => s.ratingChange);
  const [hintLoading, setHintLoading] = useState(false);

  const socketRef = useGameSocket(token, game?.game_id ?? null);

  const handleMove = useCallback(
    (uci: string) => {
      if (!socketRef.current) return;
      setThinking(true);
      setHint(null);
      socketRef.current.sendMove(uci);
    },
    [socketRef, setHint, setThinking],
  );

  const handleHint = useCallback(async () => {
    if (!token || !game) return;
    setHintLoading(true);
    setError(null);
    try {
      const response = await api.getHint(token, game.game_id);
      setHint(response);
    } catch (error) {
      const message = error instanceof ApiError ? error.detail ?? error.message : String(error);
      setError(message);
    } finally {
      setHintLoading(false);
    }
  }, [token, game, setHint, setError]);

  const handleUndo = useCallback(async () => {
    if (!token || !game) return;
    setError(null);
    try {
      const next = await api.undo(token, game.game_id);
      setGame(next);
    } catch (error) {
      const message = error instanceof ApiError ? error.detail ?? error.message : String(error);
      setError(message);
    }
  }, [token, game, setGame, setError]);

  const handleResign = useCallback(() => {
    if (!socketRef.current) return;
    socketRef.current.resign();
  }, [socketRef]);

  if (!game) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center text-surface-hint">
        Загружаем партию…
      </div>
    );
  }

  const finished = game.status !== "active";
  const statusLabel = STATUS_LABEL[game.status] ?? game.status;
  const turnLabel = finished
    ? (RESULT_LABEL[game.status] ?? statusLabel)
    : game.turn === game.user_color
      ? "Ваш ход"
      : "Ход соперника";

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-4 p-4">
      <header className="flex items-center justify-between">
        <button
          type="button"
          onClick={onLeave}
          className="text-sm font-semibold text-surface-hint hover:text-surface-text"
        >
          ← К меню
        </button>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            connected ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
          }`}
        >
          {connected ? "Online" : "Reconnect…"}
        </span>
      </header>

      <div className="flex items-center justify-between rounded-xl bg-surface-alt p-3">
        <div>
          <div className="text-xs uppercase tracking-wide text-surface-hint">{statusLabel}</div>
          <div className="text-base font-semibold text-surface-text">{turnLabel}</div>
        </div>
        <div className="text-right text-xs text-surface-hint">
          <div>Сложность: {game.difficulty}</div>
          <div>Цвет: {game.user_color === "white" ? "Белые" : "Чёрные"}</div>
        </div>
      </div>

      {finished && ratingChange !== null ? (
        <div
          className={`rounded-xl p-3 text-center text-sm font-semibold ${
            ratingChange > 0
              ? "bg-emerald-50 text-emerald-700"
              : ratingChange < 0
                ? "bg-red-50 text-red-600"
                : "bg-surface-alt text-surface-hint"
          }`}
        >
          Рейтинг: {rating}{" "}
          <span className="font-mono">
            ({ratingChange > 0 ? "+" : ""}{ratingChange})
          </span>
        </div>
      ) : null}

      <Board
        state={game}
        hintBestMove={hint?.best_move}
        onMove={handleMove}
        disabled={finished || isThinking}
      />

      {lastEngineSan && !finished ? (
        <div className="rounded-xl bg-surface-alt p-3 text-sm text-surface-text">
          Ход соперника: <span className="font-mono font-semibold">{lastEngineSan}</span>
        </div>
      ) : null}

      {errorMessage ? (
        <div className="rounded-xl border border-red-400/50 bg-red-50 p-3 text-sm text-red-600">
          {errorMessage}
        </div>
      ) : null}

      <HintPanel
        hint={hint}
        isLoading={hintLoading}
        onRequest={handleHint}
        disabled={finished}
      />

      <MoveList moves={game.moves} />

      <GameControls
        onNewGame={onLeave}
        onUndo={handleUndo}
        onResign={handleResign}
        disabled={finished}
      />
    </div>
  );
}
