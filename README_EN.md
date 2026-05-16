# Telegram Chess Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)

A full-featured Telegram bot with a **WebApp** interface for playing chess against AI powered by **Stockfish**.

> 🇷🇺 Русская версия: [README.md](README.md)

---

## Features

- Play against Stockfish (3 difficulty levels: easy / medium / hard)
- Full chessboard: drag-and-drop, legal-move highlighting, check indicator
- Best-move hint with position evaluation
- Undo, Resign, New Game controls
- Telegram `initData` authentication (HMAC-SHA256, server-side)
- Real-time position sync via WebSocket
- Backend-authoritative — every move validated server-side
- Game sessions in Redis (24h TTL by default)
- Per-user rate limiting (30 req/min)
- Full Docker stack: backend / frontend / redis / nginx

---

## Stack

### Backend
- Python 3.12, FastAPI, Uvicorn
- python-chess
- Stockfish (server-side, worker pool)
- aiogram 3 (Telegram Bot API)
- Redis 7 (game sessions, rate limiting)
- PyJWT, Pydantic v2

### Frontend
- React 18, TypeScript 5, Vite 5
- react-chessboard, chess.js
- Zustand
- TailwindCSS
- Telegram WebApp SDK

### Infrastructure
- Docker Compose
- Nginx (reverse proxy for REST + WebSocket)

---

## Quick start

### 1. Create a Telegram bot

1. Open [@BotFather](https://t.me/BotFather), send `/newbot`
2. Save the `TELEGRAM_BOT_TOKEN`
3. Register the WebApp via `/newapp` and set the public deployment URL

### 2. Clone the repo

```bash
git clone https://github.com/Mukller/chess.git
cd chess
```

### 3. Configure environment

```bash
cp .env.example .env
# Fill in:
#   TELEGRAM_BOT_TOKEN
#   TELEGRAM_BOT_USERNAME
#   TELEGRAM_WEBAPP_URL
#   APP_SECRET_KEY (32+ random chars)
```

### 4. Start the stack

```bash
docker compose up -d --build
```

Open the bot in Telegram, send `/play`, tap the **Play** button.

---

## REST API

All endpoints require `Authorization: Bearer <jwt>` (except `/api/auth/telegram`).

| Method | Path                          | Description                                 |
| ------ | ----------------------------- | ------------------------------------------- |
| POST   | `/api/auth/telegram`          | Exchange Telegram initData for access token |
| POST   | `/api/game/start`             | Start a new game                            |
| GET    | `/api/game/{game_id}`         | Get current game state                      |
| POST   | `/api/game/{game_id}/move`    | Make a move (UCI: `e2e4`, `e7e8q`)          |
| POST   | `/api/game/{game_id}/hint`    | Best-move hint + evaluation                 |
| POST   | `/api/game/{game_id}/undo`    | Undo last pair of moves                     |
| POST   | `/api/game/{game_id}/resign`  | Resign                                      |
| GET    | `/health`                     | Health check (Redis + engine + bot)         |

### WebSocket

`ws://host/ws/game/{game_id}?token=<jwt>`

Client sends: `{ "type": "move", "move": "e2e4" }`, `{ "type": "resign" }`, `{ "type": "ping" }`.

Server emits: `snapshot`, `position`, `game_over`, `error`, `pong`.

---

## Stockfish difficulty profiles

| Level   | Skill Level | Depth | Move time |
| ------- | ----------- | ----- | --------- |
| Easy    | 2           | 4     | 100 ms    |
| Medium  | 8           | 8     | 300 ms    |
| Hard    | 18          | 14    | 1200 ms   |

See [backend/app/engine/config.py](backend/app/engine/config.py).

---

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Install Stockfish: apt-get install stockfish (Linux) or https://stockfishchess.org/
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

Note: outside Telegram WebApp the login will fail because `initData` is not available.

---

## Security

- Telegram initData is validated using HMAC-SHA256 (see [backend/app/auth/telegram.py](backend/app/auth/telegram.py))
- Every move is validated server-side with python-chess — the client only sends UCI strings
- JWT bearer tokens with TTL (default 24h)
- WebSocket requires a token in the query string
- Redis sliding-window rate limiter — 30 req/min per user
- CSP and `X-Frame-Options` are configured for Telegram embedding

---

## Roadmap

- [ ] PvP (player vs player)
- [ ] ELO rating and game history (PostgreSQL)
- [ ] PGN export
- [ ] Game analysis
- [ ] Tournaments
- [ ] Puzzle / Opening trainer

See [CHANGELOG.md](CHANGELOG.md) · [RELEASE_INFO.md](RELEASE_INFO.md)

---

## Contributing

PRs and issues are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

MIT — see [LICENSE.md](LICENSE.md).

---

## Contact

- GitHub: [@Mukller](https://github.com/Mukller)
- Issues: [github.com/Mukller/chess/issues](https://github.com/Mukller/chess/issues)
