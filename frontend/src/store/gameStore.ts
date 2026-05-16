import { create } from "zustand";
import type { AuthUser, GameState, HintResponse } from "../types/game";

interface SessionState {
  token: string | null;
  user: AuthUser | null;
  setSession: (payload: { token: string; user: AuthUser }) => void;
  clearSession: () => void;
}

interface GameStoreState {
  game: GameState | null;
  lastEngineSan: string | null;
  hint: HintResponse | null;
  socketConnected: boolean;
  errorMessage: string | null;
  isThinking: boolean;
  setGame: (state: GameState | null) => void;
  applyEngineSan: (san: string | null) => void;
  setHint: (hint: HintResponse | null) => void;
  setConnected: (connected: boolean) => void;
  setError: (message: string | null) => void;
  setThinking: (value: boolean) => void;
  reset: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  token: null,
  user: null,
  setSession: ({ token, user }) => set({ token, user }),
  clearSession: () => set({ token: null, user: null }),
}));

export const useGameStore = create<GameStoreState>((set) => ({
  game: null,
  lastEngineSan: null,
  hint: null,
  socketConnected: false,
  errorMessage: null,
  isThinking: false,
  setGame: (state) => set({ game: state, hint: null }),
  applyEngineSan: (san) => set({ lastEngineSan: san }),
  setHint: (hint) => set({ hint }),
  setConnected: (connected) => set({ socketConnected: connected }),
  setError: (message) => set({ errorMessage: message }),
  setThinking: (value) => set({ isThinking: value }),
  reset: () =>
    set({
      game: null,
      lastEngineSan: null,
      hint: null,
      socketConnected: false,
      errorMessage: null,
      isThinking: false,
    }),
}));
