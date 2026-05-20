# Telegram Chess Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![aiogram 3](https://img.shields.io/badge/aiogram-3-2CA5E0.svg)](https://docs.aiogram.dev/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)

A full-featured Telegram bot for playing chess against AI powered by **Stockfish**. Fully button-driven interface right inside the chat — the board is rendered as a grid of inline buttons, no WebApp launch required. A React WebApp is included as an optional mode.

> 🇷🇺 Русская версия: [README.md](README.md)

---

## Features

- **Fully button-driven**: the only command is `/start`, everything else through keyboards
- **Play against Stockfish**: 4 difficulty levels — Easy, Medium, Hard, Expert
- **8×8 inline-button board** with coloured cells (`⬜`/`⬛`), no rank/file labels
- **Move highlights**: 🟦 selected piece · 🟢/🟩 possible move · 🟥 possible capture
- **Two-tap moves**: tap your piece → tap the target square, auto-promote pawn to queen
- **Auto-flip** when you play black
- **Player profile**: ELO rating (starts at 1200, K = 32), peak ELO, win-rate, breakdown by difficulty
- **Game history** — every finished game is recorded in Redis with settings, timestamp (MSK, UTC+3) and full move list; accessible from the profile
- Best-move hint with position evaluation (REST)
- Telegram `initData` authentication (HMAC-SHA256) — for WebApp
- Real-time position sync via WebSocket — for WebApp
- Backend-authoritative — every move validated server-side
- Per-user rate limiting (30 req/min)
- Full Docker stack: backend / frontend / redis / nginx

---

## Bot UI snapshot

```
   ┌─────────────────────────────────┐
   │   ♔ Game started                │
   │   🎯 Level: Expert              │
   │   ♔ You play: white             │
   ├─────────────────────────────────┤
   │  ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜         │  ← black pieces
   │  ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟         │
   │  ⬜ ⬛ ⬜ ⬛ ⬜ ⬛ ⬜ ⬛           │  ← empty cells coloured
   │  ⬛ ⬜ ⬛ ⬜ ⬛ ⬜ ⬛ ⬜           │
   │  ⬜ ⬛ ⬜ ⬛ 🟦 ⬛ ⬜ ⬛           │  ← selected piece
   │  ⬛ ⬜ ⬛ ⬜ 🟢 ⬜ ⬛ ⬜           │  ← possible move
   │  P  P  P  P  ⬜ P  P  P          │
   │  R  N  B  Q  K  B  N  R          │  ← white pieces (FEN letters)
   ├─────────────────────────────────┤
   │  🛑 Stop game                   │
   └─────────────────────────────────┘
```

White pieces use letters `K Q R B N P` (always legible on any theme), black pieces use filled unicode glyphs `♚ ♛ ♜ ♝ ♞ ♟`.

---

## Stack

### Backend
- Python 3.12, FastAPI, Uvicorn
- python-chess
- Stockfish (server-side, worker pool)
- aiogram 3 (Telegram Bot API)
- Redis 7 (game sessions, stats, history, rate limiting)
- PyJWT, Pydantic v2

### Frontend (optional WebApp)
- React 18, TypeScript 5, Vite 5
- react-chessboard, chess.js
- Zustand
- TailwindCSS
- Telegram WebApp SDK

### Infrastructure
- Docker Compose
- Nginx (reverse proxy for REST + WebSocket)

---

## Architecture

```
┌─────────────────────┐     ┌──────────────────────────┐
│   Telegram Client   │     │      Browser / WebApp    │
└──────────┬──────────┘     └─────────────┬────────────┘
           │                              │
           │ inline buttons               │ HTTPS + WSS
           ▼                              ▼
       ┌────────┐                    ┌─────────┐
       │  Bot   │                    │  Nginx  │
       │aiogram │                    └────┬────┘
       └────┬───┘                         │
            │                  ┌──────────┴──────────┐
            ▼                  ▼                     ▼
       ┌──────────┐      ┌───────────┐         ┌──────────┐
       │ FastAPI  │◀────▶│ FastAPI   │         │  Static  │
       │  Bot Tsk │      │ REST + WS │         │  bundle  │
       └────┬─────┘      └──────┬────┘         └──────────┘
            │                   │
            ▼                   ▼
       ┌──────────────────────────────────────────┐
       │   GameService · StatsService · History   │
       └──────┬──────────┬────────────────┬───────┘
              │          │                │
              ▼          ▼                ▼
        ┌─────────┐  ┌─────────────────┐ ┌───────────┐
        │  Redis  │  │   EnginePool    │ │  History  │
        │  games  │  │ N Stockfish proc│ │ (Redis 5y)│
        │  stats  │  └─────────────────┘ └───────────┘
        └─────────┘
```

---

## Button-driven UI

### Main menu
- `♟️ Play` · `👤 Profile`
- `❓ Help`

### Difficulty selection
- `1️⃣ Easy` · `2️⃣ Medium`
- `3️⃣ Hard` · `4️⃣ Expert`
- `⬅️ Back`

### Colour selection
- `⚪ White` · `⚫ Black`
- `🎲 Random`
- `⬅️ Back`

### In-game
- 8×8 inline board grid (tap piece → tap destination square)
- `🛑 Stop game` — below the message input

### Profile
- ELO, peak, stats, breakdown by difficulty
- `📜 Game history` — list of last 10 games with detail view (moves, time, ELO before/after)
- `🗑 Reset stats`
- `⬅️ Back`

---

## Repository layout

```
.
├── backend/                     # FastAPI app
│   ├── app/
│   │   ├── auth/                # Telegram initData + JWT
│   │   ├── bot/                 # aiogram bot + handlers (button-driven UI)
│   │   ├── engine/              # Stockfish pool + difficulty profiles
│   │   ├── game/                # GameService, StatsService, HistoryService, REST routes
│   │   ├── middleware/          # Rate limiting
│   │   ├── storage/             # Redis client
│   │   ├── ws/                  # WebSocket gateway
│   │   ├── config.py
│   │   └── main.py
│   ├── Dockerfile               # Stockfish + Python
│   └── requirements.txt
├── frontend/                    # React + Vite WebApp (optional)
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── store/
│   │   └── types/
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE.md
├── README.md
├── README_EN.md
└── RELEASE_INFO.md
```

---

## Quick start

### 1. Create a Telegram bot

1. Open [@BotFather](https://t.me/BotFather), send `/newbot`
2. Save the `TELEGRAM_BOT_TOKEN`
3. (Optional) Register the WebApp via `/setdomain` or `/newapp` and set the public deployment URL

### 2. Clone the repo

```bash
git clone https://github.com/Mukller/chess.git
cd chess
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set:
# TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_WEBAPP_URL,
# APP_SECRET_KEY (at least 32 random chars)
```

### 4. Run the stack

```bash
docker compose up -d --build
```

Services:
- `nginx` — port `80` (frontend + REST + WS)
- `api` — internal, port `8000`
- `frontend` — internal, port `80`
- `redis` — internal, port `6379`

Open the bot in Telegram and send `/start`. The rest is buttons.

### 5. Production checklist

- Put Nginx behind an HTTPS terminator (Caddy / Traefik / Let's Encrypt)
- Set `APP_ENV=production` — disables Swagger UI
- Replace `APP_SECRET_KEY` with a long random one
- Wire Prometheus/Grafana/Sentry (see [RELEASE_INFO.md](RELEASE_INFO.md))

---

## ELO system

| Parameter                  | Value                        |
| -------------------------- | ---------------------------- |
| Starting rating            | 1200                         |
| K-factor                   | 32                           |
| Opponent ELO (Easy)        | 800                          |
| Opponent ELO (Medium)      | 1400                         |
| Opponent ELO (Hard)        | 1900                         |
| Opponent ELO (Expert)      | 2400                         |
| Aborted game accounting    | counted as loss (`score = 0`)|

Formula: `delta = K * (actual - expected)`, where `expected = 1 / (1 + 10^((opp_elo - my_elo) / 400))`.

---

## REST API

All endpoints require `Authorization: Bearer <jwt>` (except `/api/auth/telegram`).

| Method | Path                          | Description                                |
| ------ | ----------------------------- | ------------------------------------------ |
| POST   | `/api/auth/telegram`          | Exchange Telegram initData for access token|
| POST   | `/api/game/start`             | Create a new game                          |
| GET    | `/api/game/{game_id}`         | Get current game state                     |
| POST   | `/api/game/{game_id}/move`    | Make a move (UCI: `e2e4`, `e7e8q`)         |
| POST   | `/api/game/{game_id}/hint`    | Best-move hint + position evaluation       |
| POST   | `/api/game/{game_id}/undo`    | Undo the last pair of moves                |
| POST   | `/api/game/{game_id}/resign`  | Resign                                     |
| GET    | `/health`                     | Health check (Redis + engine + bot)        |

### WebSocket

`ws://host/ws/game/{game_id}?token=<jwt>`

Client sends: `{ "type": "move", "move": "e2e4" }`, `{ "type": "resign" }`, `{ "type": "ping" }`.

Server sends:
- `{ "type": "snapshot", "state": {...} }` — on connect
- `{ "type": "position", "state": {...}, "player_move": "e2e4", "engine_move": {...} }`
- `{ "type": "game_over", "result": "1-0", "status": "checkmate" }`
- `{ "type": "error", "detail": "..." }`

---

## Stockfish difficulty levels

| Level   | Skill Level | Depth | Move time | Opponent ELO |
| ------- | ----------- | ----- | --------- | ------------ |
| Easy    | 2           | 4     | 100 ms    | ~800         |
| Medium  | 8           | 8     | 300 ms    | ~1400        |
| Hard    | 18          | 14    | 1200 ms   | ~1900        |
| Expert  | 20          | 22    | 3000 ms   | ~2400        |

Configuration in [backend/app/engine/config.py](backend/app/engine/config.py).

---

## Data storage

| Redis key                    | TTL       | Content                                       |
| ---------------------------- | --------- | --------------------------------------------- |
| `game:{id}`                  | 24 h      | Active game (FEN, moves, status)              |
| `user:{id}:games`            | 24 h      | Active-game index for user                    |
| `user:{id}:stats`            | 5 years   | ELO, win-rate, breakdown by difficulty        |
| `user:{id}:history`          | 5 years   | Finished-game index (sorted set)              |
| `game_history:{id}`          | 5 years   | Finished game record (full move log)          |
| `rl:{user}:{window}`         | 60 s      | Sliding window for rate limiting              |

Each history record stores: settings (difficulty, colour), start/finish timestamp in **MSK (UTC+3)**, full UCI move list, final FEN, ELO before and after, result.

---

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Install stockfish: apt-get install stockfish or https://stockfishchess.org/
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

Auth requires a valid Telegram `initData`, so the WebApp won't authenticate outside Telegram. The Telegram bot itself can be tested directly in the chat via `/start`.

---

## Security

- Telegram initData validated via HMAC-SHA256 (see [backend/app/auth/telegram.py](backend/app/auth/telegram.py))
- All moves validated server-side via python-chess — the client only submits UCI
- JWT with TTL (24 h by default)
- WebSocket requires a token in the query string
- Redis-based rate limiting (sliding window) — 30 req/min per user
- CSP and `X-Frame-Options` set for Telegram embedding

---

## Roadmap

- [x] Button-driven UI, no commands
- [x] 4 difficulty levels (including Expert)
- [x] ELO rating and player profile
- [x] Game history with replay
- [ ] PvP (player vs player)
- [ ] PGN export
- [ ] Engine analysis of finished games
- [ ] Tournaments
- [ ] Puzzle / Opening trainer

More: [CHANGELOG.md](CHANGELOG.md) · [RELEASE_INFO.md](RELEASE_INFO.md)

---

## Contributing

PRs and issues are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

MIT — see [LICENSE.md](LICENSE.md).

---

## Contacts

- GitHub: [@Mukller](https://github.com/Mukller)
- Issues: [github.com/Mukller/chess/issues](https://github.com/Mukller/chess/issues)
