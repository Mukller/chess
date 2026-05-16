interface Props {
  onNewGame: () => void;
  onUndo: () => void;
  onResign: () => void;
  disabled: boolean;
}

export function GameControls({ onNewGame, onUndo, onResign, disabled }: Props) {
  return (
    <div className="grid grid-cols-3 gap-2">
      <button
        type="button"
        onClick={onNewGame}
        className="rounded-xl bg-accent px-3 py-2 text-sm font-semibold text-accent-fg shadow"
      >
        Новая
      </button>
      <button
        type="button"
        onClick={onUndo}
        disabled={disabled}
        className="rounded-xl border border-accent/40 bg-surface-alt px-3 py-2 text-sm font-semibold text-surface-text disabled:opacity-50"
      >
        Откатить
      </button>
      <button
        type="button"
        onClick={onResign}
        disabled={disabled}
        className="rounded-xl border border-red-400/50 bg-surface-alt px-3 py-2 text-sm font-semibold text-red-500 disabled:opacity-50"
      >
        Сдаться
      </button>
    </div>
  );
}
