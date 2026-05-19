import { useState } from "react";

import { ColorSelector } from "../components/ColorSelector";
import { DifficultySelector } from "../components/DifficultySelector";
import { useSessionStore } from "../store/gameStore";
import type { Color, Difficulty } from "../types/game";

interface Props {
  starting: boolean;
  errorMessage: string | null;
  onStart: (options: { difficulty: Difficulty; user_color: Color }) => void;
}

export function HomePage({ starting, errorMessage, onStart }: Props) {
  const [difficulty, setDifficulty] = useState<Difficulty>("medium");
  const [color, setColor] = useState<Color>("white");
  const rating = useSessionStore((s) => s.rating);

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-6 p-4">
      <header className="text-center">
        <div className="text-4xl">♟</div>
        <h1 className="mt-2 text-xl font-bold text-surface-text">Шахматы против Stockfish</h1>
        <p className="mt-1 text-sm font-semibold text-surface-hint">
          Рейтинг: <span className="text-surface-text">{rating}</span>
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-surface-hint">Сложность</h2>
        <DifficultySelector value={difficulty} onChange={setDifficulty} />
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-surface-hint">Ваш цвет</h2>
        <ColorSelector value={color} onChange={setColor} />
      </section>

      {errorMessage ? (
        <div className="rounded-xl border border-red-400/50 bg-red-50 p-3 text-sm text-red-600">
          {errorMessage}
        </div>
      ) : null}

      <button
        type="button"
        onClick={() => onStart({ difficulty, user_color: color })}
        disabled={starting}
        className="rounded-xl bg-accent px-4 py-3 text-base font-semibold text-accent-fg shadow disabled:opacity-50"
      >
        {starting ? "Создаём партию…" : "Начать партию"}
      </button>
    </div>
  );
}
