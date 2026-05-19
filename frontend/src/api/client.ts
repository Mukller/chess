import type {
  Color,
  Difficulty,
  GameState,
  HintResponse,
  LoginResponse,
  MoveResponse,
} from "../types/game";

const RAW_API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
export const API_BASE = RAW_API_BASE.endsWith("/api")
  ? RAW_API_BASE
  : `${RAW_API_BASE.replace(/\/$/, "")}/api`;

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { token?: string | null } = {},
): Promise<T> {
  const { token, headers, ...rest } = init;
  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers || {}),
    },
  });
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const data = await response.json();
      detail = typeof data?.detail === "string" ? data.detail : JSON.stringify(data);
    } catch {
      detail = await response.text();
    }
    throw new ApiError(
      `request failed (${response.status})`,
      response.status,
      detail,
    );
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  loginAnonymous(deviceId: string): Promise<LoginResponse> {
    return request<LoginResponse>("/auth/anonymous", {
      method: "POST",
      body: JSON.stringify({ device_id: deviceId }),
    });
  },

  startGame(
    token: string,
    payload: { difficulty: Difficulty; user_color: Color },
  ): Promise<GameState> {
    return request<GameState>("/game/start", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    });
  },

  getGame(token: string, gameId: string): Promise<GameState> {
    return request<GameState>(`/game/${gameId}`, { token });
  },

  makeMove(token: string, gameId: string, move: string): Promise<MoveResponse> {
    return request<MoveResponse>(`/game/${gameId}/move`, {
      method: "POST",
      token,
      body: JSON.stringify({ move }),
    });
  },

  getHint(token: string, gameId: string): Promise<HintResponse> {
    return request<HintResponse>(`/game/${gameId}/hint`, {
      method: "POST",
      token,
    });
  },

  undo(token: string, gameId: string): Promise<GameState> {
    return request<GameState>(`/game/${gameId}/undo`, {
      method: "POST",
      token,
    });
  },

  resign(token: string, gameId: string): Promise<GameState> {
    return request<GameState>(`/game/${gameId}/resign`, {
      method: "POST",
      token,
    });
  },
};
