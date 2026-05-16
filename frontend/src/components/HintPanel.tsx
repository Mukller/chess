import type { HintResponse } from "../types/game";

interface Props {
  hint: HintResponse | null;
  isLoading: boolean;
  onRequest: () => void;
  disabled: boolean;
}

function formatScore(hint: HintResponse): string {
  if (hint.mate_in !== null && hint.mate_in !== undefined) {
    return `мат через ${Math.abs(hint.mate_in)}`;
  }
  if (hint.evaluation === null || hint.evaluation === undefined) return "—";
  return hint.evaluation > 0 ? `+${hint.evaluation.toFixed(2)}` : hint.evaluation.toFixed(2);
}

export function HintPanel({ hint, isLoading, onRequest, disabled }: Props) {
  return (
    <div className="space-y-2 rounded-xl bg-surface-alt p-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-surface-text">Подсказка</h3>
        <button
          type="button"
          onClick={onRequest}
          disabled={disabled || isLoading}
          className="rounded-lg bg-accent px-3 py-1 text-xs font-semibold text-accent-fg disabled:opacity-50"
        >
          {isLoading ? "Анализ…" : "Получить"}
        </button>
      </div>
      {hint ? (
        <div className="space-y-1 text-sm">
          <div>
            Лучший ход:{" "}
            <span className="font-mono font-semibold text-surface-text">{hint.best_move}</span>
          </div>
          <div className="text-surface-hint">
            Оценка: <span className="font-mono">{formatScore(hint)}</span>
            {hint.depth ? ` · глубина ${hint.depth}` : null}
          </div>
        </div>
      ) : (
        <p className="text-xs text-surface-hint">
          Запросите подсказку — движок предложит лучший ход в текущей позиции.
        </p>
      )}
    </div>
  );
}
