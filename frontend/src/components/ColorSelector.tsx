import type { Color } from "../types/game";

interface Props {
  value: Color;
  onChange: (value: Color) => void;
}

export function ColorSelector({ value, onChange }: Props) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {(["white", "black"] as Color[]).map((color) => {
        const active = color === value;
        return (
          <button
            key={color}
            type="button"
            onClick={() => onChange(color)}
            className={`flex items-center gap-2 rounded-xl border p-3 text-left transition ${
              active
                ? "border-accent bg-accent text-accent-fg shadow"
                : "border-transparent bg-surface-alt text-surface-text hover:border-accent/40"
            }`}
          >
            <span className="text-2xl" aria-hidden>
              {color === "white" ? "♔" : "♚"}
            </span>
            <span className="text-sm font-semibold">
              {color === "white" ? "Белые" : "Чёрные"}
            </span>
          </button>
        );
      })}
    </div>
  );
}
