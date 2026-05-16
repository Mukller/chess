import { useCallback, useMemo } from "react";
import { Chess, type Square } from "chess.js";
import { Chessboard } from "react-chessboard";

import type { Color, GameState } from "../types/game";

interface Props {
  state: GameState;
  hintBestMove?: string | null;
  onMove: (uci: string) => void;
  disabled: boolean;
}

function squareStyle(color: string): Record<string, string> {
  return {
    background: color,
    boxShadow: "inset 0 0 0 2px rgba(255,255,255,0.6)",
  };
}

function highlightForCheck(board: Chess): Record<string, Record<string, string>> {
  if (!board.isCheck()) return {};
  const turn = board.turn();
  const kingSquare = board
    .board()
    .flat()
    .find((piece) => piece && piece.type === "k" && piece.color === turn)?.square;
  if (!kingSquare) return {};
  return { [kingSquare]: squareStyle("rgba(220, 38, 38, 0.45)") };
}

function highlightLastMove(state: GameState): Record<string, Record<string, string>> {
  const last = state.moves[state.moves.length - 1];
  if (!last) return {};
  const from = last.slice(0, 2);
  const to = last.slice(2, 4);
  return {
    [from]: squareStyle("rgba(34, 211, 238, 0.35)"),
    [to]: squareStyle("rgba(34, 211, 238, 0.55)"),
  };
}

function highlightHint(uci: string | null | undefined): Record<string, Record<string, string>> {
  if (!uci) return {};
  return {
    [uci.slice(0, 2)]: squareStyle("rgba(250, 204, 21, 0.6)"),
    [uci.slice(2, 4)]: squareStyle("rgba(250, 204, 21, 0.6)"),
  };
}

function boardOrientation(color: Color): "white" | "black" {
  return color === "white" ? "white" : "black";
}

export function Board({ state, hintBestMove, onMove, disabled }: Props) {
  const board = useMemo(() => new Chess(state.fen), [state.fen]);

  const customSquareStyles = useMemo(
    () => ({
      ...highlightLastMove(state),
      ...highlightForCheck(board),
      ...highlightHint(hintBestMove),
    }),
    [state, board, hintBestMove],
  );

  const isPlayersTurn = state.turn === state.user_color && state.status === "active";

  const handlePieceDrop = useCallback(
    (from: string, to: string, piece: string) => {
      if (disabled || !isPlayersTurn) return false;
      const promotion = piece[1]?.toLowerCase() === "p" && (to[1] === "8" || to[1] === "1") ? "q" : undefined;
      const candidate = `${from}${to}${promotion ?? ""}`;
      if (!state.legal_moves.includes(candidate)) return false;
      onMove(candidate);
      return true;
    },
    [disabled, isPlayersTurn, state.legal_moves, onMove],
  );

  const isDraggablePiece = useCallback(
    ({ piece }: { piece: string }) => {
      if (disabled || !isPlayersTurn) return false;
      return piece.startsWith(state.user_color === "white" ? "w" : "b");
    },
    [disabled, isPlayersTurn, state.user_color],
  );

  return (
    <div className="aspect-square w-full">
      <Chessboard
        position={state.fen}
        boardOrientation={boardOrientation(state.user_color)}
        arePiecesDraggable={!disabled && isPlayersTurn}
        isDraggablePiece={isDraggablePiece}
        onPieceDrop={(from, to, piece) => handlePieceDrop(from as Square, to as Square, piece)}
        customSquareStyles={customSquareStyles}
        customBoardStyle={{
          borderRadius: 12,
          boxShadow: "0 18px 40px rgba(15,23,42,0.35)",
        }}
        customDarkSquareStyle={{ backgroundColor: "#b58863" }}
        customLightSquareStyle={{ backgroundColor: "#f0d9b5" }}
      />
    </div>
  );
}
