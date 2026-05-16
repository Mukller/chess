import { useMemo } from "react";
import { Chess } from "chess.js";

interface Props {
  moves: string[];
}

export function MoveList({ moves }: Props) {
  const sanRows = useMemo(() => {
    const board = new Chess();
    const rendered: Array<{ ply: number; white: string; black?: string }> = [];
    let bucket: { ply: number; white: string; black?: string } | null = null;
    moves.forEach((uci, index) => {
      try {
        const move = board.move({
          from: uci.slice(0, 2),
          to: uci.slice(2, 4),
          promotion: uci.length === 5 ? uci.slice(4) : undefined,
        });
        const san = move?.san ?? uci;
        if (index % 2 === 0) {
          bucket = { ply: index / 2 + 1, white: san };
          rendered.push(bucket);
        } else if (bucket) {
          bucket.black = san;
        }
      } catch {
        // skip invalid moves silently — backend is authoritative
      }
    });
    return rendered;
  }, [moves]);

  if (sanRows.length === 0) {
    return (
      <div className="rounded-xl bg-surface-alt p-3 text-sm text-surface-hint">
        Ходы появятся здесь после первого хода.
      </div>
    );
  }

  return (
    <ol className="grid grid-cols-[auto_1fr_1fr] gap-x-3 gap-y-1 rounded-xl bg-surface-alt p-3 font-mono text-sm">
      {sanRows.map((row) => (
        <li key={row.ply} className="contents">
          <span className="text-surface-hint">{row.ply}.</span>
          <span>{row.white}</span>
          <span>{row.black ?? ""}</span>
        </li>
      ))}
    </ol>
  );
}
