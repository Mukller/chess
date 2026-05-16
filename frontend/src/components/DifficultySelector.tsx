import type { Difficulty } from "../types/game";

interface Props {
  value: Difficulty;
  onChange: (value: Difficulty) => void;
}

const LABELS: Record<Difficulty, string> = {
  easy: "Лёгкий",
  medium: "Средний",
  hard: "Сложный",
};

const SUBLINES: Record<Difficulty, string> = {
  easy: "Skill 2 · 100 мс",
  medium: "Skill 8 · 300 мс",
  hard: "Skill 18 · 1.2 с",
};

export function DifficultySelector({ value, onChange }: Props) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {(Object.keys(LABELS) as Difficulty[]).map((option) => {
        const active = option === value;
        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={`rounded-xl border p-3 text-left transition ${
              active
                ? "border-accent bg-accent text-accent-fg shadow"
                : "border-transparent bg-surface-alt text-surface-text hover:border-accent/40"
            }`}
          >
            <div className="text-sm font-semibold">{LABELS[option]}</div>
            <div className={`text-xs ${active ? "text-accent-fg/80" : "text-surface-hint"}`}>
              {SUBLINES[option]}
            </div>
          </button>
        );
      })}
    </div>
  );
}
