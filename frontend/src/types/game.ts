export type Difficulty = "easy" | "medium" | "hard";
export type Color = "white" | "black";
export type GameStatus =
  | "active"
  | "checkmate"
  | "stalemate"
  | "draw"
  | "resigned"
  | "abandoned";

export interface GameState {
  game_id: string;
  fen: string;
  moves: string[];
  difficulty: Difficulty;
  user_color: Color;
  status: GameStatus;
  result: string | null;
  last_engine_move: string | null;
  turn: Color;
  is_check: boolean;
  legal_moves: string[];
  created_at: number;
  updated_at: number;
}

export interface EngineMoveSummary {
  uci: string;
  san: string | null;
}

export interface MoveResponse {
  state: GameState;
  player_move: string;
  engine_move: EngineMoveSummary | null;
}

export interface HintResponse {
  best_move: string;
  evaluation: number | null;
  mate_in: number | null;
  depth: number | null;
}

export interface AuthUser {
  id: number;
  first_name: string;
  last_name?: string | null;
  username?: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
