import { create } from "zustand";
import type { AuthUser, GameState, HintResponse } from "../types/game";

interface SessionState {
  token: string | null;
  user: AuthUser | null;
  rating: number;
  setSession: (payload: { token: string; user: AuthUser }) => void;
  setRating: (rating: number) => void;
  clearSession: () => void;
}

interface GameStoreState {
  game: GameState | null;
  lastEngineSan: string | null;
  hint: HintResponse | null;
  socketConnected: boolean;
  errorMessage: string | null;
  isThinking: boolean;
  ratingChange: number | null;
  setGame: (state: GameState | null) => void;
  applyEngineSan: (san: string | null) => void;
  setHint: (hint: HintResponse | null) => void;
  setConnected: (connected: boolean) => void;
  setError: (message: string | null) => void;
  setThinking: (value: boolean) => void;
  setRatingChange: (change: number | null) => void;
  reset: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  token: null,
  user: null,
  rating: 1200,
  setSession: ({ token, user }) => set({ token, user }),
  setRating: (rating) => set({ rating }),
  clearSession: () => set({ token: null, user: null, rating: 1200 }),
}));

export const useGameStore = create<GameStoreState>((set) => ({
  game: null,
  lastEngineSan: null,
  hint: null,
  socketConnected: false,
  errorMessage: null,
  isThinking: false,
  ratingChange: null,
  setGame: (state) => set({ game: state, hint: null }),
  applyEngineSan: (san) => set({ lastEngineSan: san }),
  setHint: (hint) => set({ hint }),
  setConnected: (connected) => set({ socketConnected: connected }),
  setError: (message) => set({ errorMessage: message }),
  setThinking: (value) => set({ isThinking: value }),
  setRatingChange: (change) => set({ ratingChange: change }),
  reset: () =>
    set({
      game: null,
      lastEngineSan: null,
      hint: null,
      socketConnected: false,
      errorMessage: null,
      isThinking: false,
      ratingChange: null,
    }),
}));
