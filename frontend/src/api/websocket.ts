import type { GameState } from "../types/game";

const RAW_WS_BASE = import.meta.env.VITE_WS_BASE_URL || deriveDefaultWsBase();

function deriveDefaultWsBase(): string {
  if (typeof window === "undefined") return "";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}`;
}

export type ServerEvent =
  | { type: "snapshot"; protocol: number; state: GameState; rating: number }
  | {
      type: "position";
      state: GameState;
      player_move: string;
      engine_move: { uci: string; san: string | null } | null;
    }
  | { type: "game_over"; result: string | null; status: string; rating: number; rating_change: number }
  | { type: "error"; detail: string }
  | { type: "pong" };

export interface GameSocketHandlers {
  onEvent: (event: ServerEvent) => void;
  onOpen?: () => void;
  onClose?: (code: number) => void;
}

export class GameSocket {
  private socket?: WebSocket;
  private reconnectAttempts = 0;
  private closedByUser = false;
  private pingTimer?: number;

  constructor(
    private readonly gameId: string,
    private readonly token: string,
    private readonly handlers: GameSocketHandlers,
  ) {}

  connect(): void {
    this.closedByUser = false;
    const url = `${RAW_WS_BASE.replace(/\/$/, "")}/ws/game/${this.gameId}?token=${encodeURIComponent(this.token)}`;
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.handlers.onOpen?.();
      this.pingTimer = window.setInterval(() => {
        this.send({ type: "ping" });
      }, 25_000);
    };

    this.socket.onmessage = (raw) => {
      try {
        const data = JSON.parse(raw.data) as ServerEvent;
        this.handlers.onEvent(data);
      } catch (error) {
        console.error("[ws] invalid payload", error);
      }
    };

    this.socket.onclose = (event) => {
      window.clearInterval(this.pingTimer);
      this.handlers.onClose?.(event.code);
      if (!this.closedByUser && event.code !== 1008) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = (event) => {
      console.warn("[ws] error", event);
    };
  }

  send(payload: Record<string, unknown>): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  sendMove(move: string): void {
    this.send({ type: "move", move });
  }

  resign(): void {
    this.send({ type: "resign" });
  }

  close(): void {
    this.closedByUser = true;
    window.clearInterval(this.pingTimer);
    this.socket?.close(1000, "client closed");
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts += 1;
    const delay = Math.min(15_000, 500 * 2 ** this.reconnectAttempts);
    window.setTimeout(() => {
      if (!this.closedByUser) this.connect();
    }, delay);
  }
}
