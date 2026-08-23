# Telegram Chess Bot

<p align="center">
  <a href="https://github.com/Mukller">
    <img src="https://img.shields.io/badge/Anton%20Petnitsky-Developer-0d1117?style=for-the-badge&logo=github&logoColor=white&labelColor=0d1117&color=58a6ff" alt="Anton Petnitsky" />
  </a>
</p>
- Issues: [github.com/Mukller/chess/issues](https://github.com/Mukller/chess/issues)
<div align="center">

**English** вЂў [Р СѓСЃСЃРєРёР№](README.md)

</div>

# Telegram Chess Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![aiogram 3](https://img.shields.io/badge/aiogram-3-2CA5E0.svg)](https://docs.aiogram.dev/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)

A full-featured Telegram bot for playing chess against AI powered by **Stockfish**. Fully button-driven interface right inside the chat тАФ the board is rendered as a grid of inline buttons, no WebApp launch required. A React WebApp is included as an optional mode.

> ЁЯЗ╖ЁЯЗ║ ╨а╤Г╤Б╤Б╨║╨░╤П ╨▓╨╡╤А╤Б╨╕╤П: [README.md](README.md)

<p align="center">
  <img src="assets/screenshot.png" alt="Game screen: board, hint panel, move history" width="420" />
</p>

---

## Features

- **Fully button-driven**: the only command is `/start`, everything else through keyboards
- **Three game modes**:
  - ЁЯдЦ **Vs Stockfish** тАФ 8 difficulty levels from Beginner to Grandmaster
  - ЁЯСе **Hot-seat** тАФ two players on the same device, board flips after every move
  - ЁЯМР **Online PvP** тАФ play with a friend using a 6-char invite code (beta)
- **Piece glyphs for both colours**: white `тЩФтЩХтЩЦтЩЧтЩШтЩЩ`, black `тЩЪтЩЫтЩЬтЩЭтЩЮтЩЯ`
- **8├Ч8 inline-button board**, no rank/file labels
- **Move highlights**: ЁЯЯж selected piece ┬╖ ЁЯЯв possible move ┬╖ ЁЯЯе possible capture
- **Two-tap moves**: tap your piece тЖТ tap the target square, auto-promote pawn to queen
- **Auto-flip** when you play black
- **Stable board refresh** тАФ `message is not modified` errors suppressed, every move bumps a counter to guarantee a redraw
- **Player profile**: ELO rating (starts at 1200, K = 32), peak ELO, win-rate, breakdown by difficulty
- **Game history** тАФ every finished game is recorded in Redis with settings, timestamp (MSK, UTC+3) and full move list; accessible from the profile
- Best-move hint with position evaluation (REST)
- Telegram `initData` authentication (HMAC-SHA256) тАФ for WebApp
- Real-time position sync via WebSocket тАФ for WebApp
- Backend-authoritative тАФ every move validated server-side
- Per-user rate limiting (30 req/min)
- Full Docker stack: backend / frontend / redis / nginx

---

## Bot UI snapshot

```
   тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
   тФВ   тЩФ Game started                тФВ
   тФВ   ЁЯОп Level: Expert              тФВ
   тФВ   тЩФ You play: white             тФВ
   тФЬтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФд
   тФВ  тЩЬ  тЩЮ  тЩЭ  тЩЫ  тЩЪ  тЩЭ  тЩЮ  тЩЬ         тФВ  тЖР black pieces
   тФВ  тЩЯ  тЩЯ  тЩЯ  тЩЯ  тЩЯ  тЩЯ  тЩЯ  тЩЯ         тФВ
   тФВ  тмЬ тмЫ тмЬ тмЫ тмЬ тмЫ тмЬ тмЫ           тФВ  тЖР empty cells coloured
   тФВ  тмЫ тмЬ тмЫ тмЬ тмЫ тмЬ тмЫ тмЬ           тФВ
   тФВ  тмЬ тмЫ тмЬ тмЫ ЁЯЯж тмЫ тмЬ тмЫ           тФВ  тЖР selected piece
   тФВ  тмЫ тмЬ тмЫ тмЬ ЁЯЯв тмЬ тмЫ тмЬ           тФВ  тЖР possible move
   тФВ  P  P  P  P  тмЬ P  P  P          тФВ
   тФВ  R  N  B  Q  K  B  N  R          тФВ  тЖР white pieces (FEN letters)
   тФЬтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФд
   тФВ  ЁЯЫС Stop game                   тФВ
   тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ
```

White pieces use letters `K Q R B N P` (always legible on any theme), black pieces use filled unicode glyphs `тЩЪ тЩЫ тЩЬ тЩЭ тЩЮ тЩЯ`.

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
тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР     тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
тФВ   Telegram Client   тФВ     тФВ      Browser / WebApp    тФВ
тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ     тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ
           тФВ                              тФВ
           тФВ inline buttons               тФВ HTTPS + WSS
           тЦ╝                              тЦ╝
       тФМтФАтФАтФАтФАтФАтФАтФАтФАтФР                    тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
       тФВ  Bot   тФВ                    тФВ  Nginx  тФВ
       тФВaiogram тФВ                    тФФтФАтФАтФАтФАтФмтФАтФАтФАтФАтФШ
       тФФтФАтФАтФАтФАтФмтФАтФАтФАтФШ                         тФВ
            тФВ                  тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФ┤тФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
            тЦ╝                  тЦ╝                     тЦ╝
       тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР      тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР         тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
       тФВ FastAPI  тФВтЧАтФАтФАтФАтФАтЦ╢тФВ FastAPI   тФВ         тФВ  Static  тФВ
       тФВ  Bot Tsk тФВ      тФВ REST + WS тФВ         тФВ  bundle  тФВ
       тФФтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФШ      тФФтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФШ         тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ
            тФВ                   тФВ
            тЦ╝                   тЦ╝
       тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
       тФВ   GameService ┬╖ StatsService ┬╖ History   тФВ
       тФФтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФмтФАтФАтФАтФАтФАтФАтФАтФШ
              тФВ          тФВ                тФВ
              тЦ╝          тЦ╝                тЦ╝
        тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР  тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР тФМтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФР
        тФВ  Redis  тФВ  тФВ   EnginePool    тФВ тФВ  History  тФВ
        тФВ  games  тФВ  тФВ N Stockfish procтФВ тФВ (Redis 5y)тФВ
        тФВ  stats  тФВ  тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ
        тФФтФАтФАтФАтФАтФАтФАтФАтФАтФАтФШ
```

---

## Button-driven UI

### Main menu
- `тЩЯя╕П Play` ┬╖ `ЁЯСд Profile`
- `тЭУ Help`

### Difficulty selection
- `1я╕ПтГг Easy` ┬╖ `2я╕ПтГг Medium`
- `3я╕ПтГг Hard` ┬╖ `4я╕ПтГг Expert`
- `тмЕя╕П Back`

### Colour selection
- `тЪк White` ┬╖ `тЪл Black`
- `ЁЯО▓ Random`
- `тмЕя╕П Back`

### In-game
- 8├Ч8 inline board grid (tap piece тЖТ tap destination square)
- `ЁЯЫС Stop game` тАФ below the message input

### Profile
- ELO, peak, stats, breakdown by difficulty
- `ЁЯУЬ Game history` тАФ list of last 10 games with detail view (moves, time, ELO before/after)
- `ЁЯЧС Reset stats`
- `тмЕя╕П Back`

---

## Repository layout

```
.
тФЬтФАтФА backend/                     # FastAPI app
тФВ   тФЬтФАтФА app/
тФВ   тФВ   тФЬтФАтФА auth/                # Telegram initData + JWT
тФВ   тФВ   тФЬтФАтФА bot/                 # aiogram bot + handlers (button-driven UI)
тФВ   тФВ   тФЬтФАтФА engine/              # Stockfish pool + difficulty profiles
тФВ   тФВ   тФЬтФАтФА game/                # GameService, StatsService, HistoryService, REST routes
тФВ   тФВ   тФЬтФАтФА middleware/          # Rate limiting
тФВ   тФВ   тФЬтФАтФА storage/             # Redis client
тФВ   тФВ   тФЬтФАтФА ws/                  # WebSocket gateway
тФВ   тФВ   тФЬтФАтФА config.py
тФВ   тФВ   тФФтФАтФА main.py
тФВ   тФЬтФАтФА Dockerfile               # Stockfish + Python
тФВ   тФФтФАтФА requirements.txt
тФЬтФАтФА frontend/                    # React + Vite WebApp (optional)
тФВ   тФЬтФАтФА src/
тФВ   тФВ   тФЬтФАтФА api/
тФВ   тФВ   тФЬтФАтФА components/
тФВ   тФВ   тФЬтФАтФА hooks/
тФВ   тФВ   тФЬтФАтФА pages/
тФВ   тФВ   тФЬтФАтФА store/
тФВ   тФВ   тФФтФАтФА types/
тФВ   тФЬтФАтФА Dockerfile
тФВ   тФФтФАтФА package.json
тФЬтФАтФА nginx/
тФВ   тФФтФАтФА nginx.conf
тФЬтФАтФА docker-compose.yml
тФЬтФАтФА .env.example
тФЬтФАтФА CHANGELOG.md
тФЬтФАтФА CODE_OF_CONDUCT.md
тФЬтФАтФА CONTRIBUTING.md
тФЬтФАтФА LICENSE.md
тФЬтФАтФА README.md
тФЬтФАтФА README_EN.md
тФФтФАтФА RELEASE_INFO.md
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
- `nginx` тАФ port `80` (frontend + REST + WS)
- `api` тАФ internal, port `8000`
- `frontend` тАФ internal, port `80`
- `redis` тАФ internal, port `6379`

Open the bot in Telegram and send `/start`. The rest is buttons.

### 5. Production checklist

- Put Nginx behind an HTTPS terminator (Caddy / Traefik / Let's Encrypt)
- Set `APP_ENV=production` тАФ disables Swagger UI
- Replace `APP_SECRET_KEY` with a long random one
- Wire Prometheus/Grafana/Sentry (see [RELEASE_INFO.md](RELEASE_INFO.md))

---

## ELO system

| Parameter                  | Value                        |
| -------------------------- | ---------------------------- |
| Starting rating            | 1200                         |
| K-factor                   | 32                           |
| Opponent ELO (Beginner)        | 500                      |
| Opponent ELO (Easy)            | 800                      |
| Opponent ELO (Casual)          | 1100                     |
| Opponent ELO (Medium)          | 1400                     |
| Opponent ELO (Advanced)        | 1700                     |
| Opponent ELO (Hard)            | 1900                     |
| Opponent ELO (Expert)          | 2200                     |
| Opponent ELO (Grandmaster)     | 2600                     |
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
- `{ "type": "snapshot", "state": {...} }` тАФ on connect
- `{ "type": "position", "state": {...}, "player_move": "e2e4", "engine_move": {...} }`
- `{ "type": "game_over", "result": "1-0", "status": "checkmate" }`
- `{ "type": "error", "detail": "..." }`

---

## Stockfish difficulty levels

| Level            | Skill Level | Depth | Move time | Opponent ELO |
| ---------------- | ----------- | ----- | --------- | ------------ |
| Beginner ЁЯРг      | 0           | 2     | 80 ms     | ~500         |
| Easy             | 3           | 4     | 150 ms    | ~800         |
| Casual           | 6           | 6     | 250 ms    | ~1100        |
| Medium           | 10          | 8     | 400 ms    | ~1400        |
| Advanced         | 14          | 11    | 700 ms    | ~1700        |
| Hard             | 17          | 14    | 1200 ms   | ~1900        |
| Expert           | 20          | 18    | 2500 ms   | ~2200        |
| Grandmaster ЁЯСС   | 20          | 24    | 5000 ms   | ~2600        |

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
- All moves validated server-side via python-chess тАФ the client only submits UCI
- JWT with TTL (24 h by default)
- WebSocket requires a token in the query string
- Redis-based rate limiting (sliding window) тАФ 30 req/min per user
- CSP and `X-Frame-Options` set for Telegram embedding

---

## Roadmap

- [x] Button-driven UI, no commands
- [x] 8 difficulty levels (Beginner тЖТ Grandmaster)
- [x] ELO rating and player profile
- [x] Game history with replay
- [x] Hot-seat (two players on one device)
- [x] Online PvP with invite codes (beta тАФ sync on click)
- [ ] Live online PvP with pub/sub push notifications
- [ ] PGN export
- [ ] Engine analysis of finished games
- [ ] Tournaments
- [ ] Puzzle / Opening trainer

More: [CHANGELOG.md](CHANGELOG.md) ┬╖ [RELEASE_INFO.md](RELEASE_INFO.md)

---

## Contributing

PRs and issues are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

MIT тАФ see [LICENSE.md](LICENSE.md).

---

## Contacts

- GitHub: [@Mukller](https://github.com/Mukller)
- Issues: [github.com/Mukller/chess/issues](https://github.com/Mukller/chess/issues)