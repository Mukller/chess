<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/chess)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

</div>

<details open>
<summary><strong>📖 English</strong></summary>

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
- **Three game modes**:
  - 🤖 **Vs Stockfish** — 8 difficulty levels from Beginner to Grandmaster
  - 👥 **Hot-seat** — two players on the same device, board flips after every move
  - 🌐 **Online PvP** — play with a friend using a 6-char invite code (beta)
- **Piece glyphs for both colours**: white `♔♕♖♗♘♙`, black `♚♛♜♝♞♟`
- **8×8 inline-button board**, no rank/file labels
- **Move highlights**: 🟦 selected piece · 🟢 possible move · 🟥 possible capture
- **Two-tap moves**: tap your piece → tap the target square, auto-promote pawn to queen
- **Auto-flip** when you play black
- **Stable board refresh** — `message is not modified` errors suppressed, every move bumps a counter to guarantee a redraw
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
- `{ "type": "snapshot", "state": {...} }` — on connect
- `{ "type": "position", "state": {...}, "player_move": "e2e4", "engine_move": {...} }`
- `{ "type": "game_over", "result": "1-0", "status": "checkmate" }`
- `{ "type": "error", "detail": "..." }`

---

## Stockfish difficulty levels

| Level            | Skill Level | Depth | Move time | Opponent ELO |
| ---------------- | ----------- | ----- | --------- | ------------ |
| Beginner 🐣      | 0           | 2     | 80 ms     | ~500         |
| Easy             | 3           | 4     | 150 ms    | ~800         |
| Casual           | 6           | 6     | 250 ms    | ~1100        |
| Medium           | 10          | 8     | 400 ms    | ~1400        |
| Advanced         | 14          | 11    | 700 ms    | ~1700        |
| Hard             | 17          | 14    | 1200 ms   | ~1900        |
| Expert           | 20          | 18    | 2500 ms   | ~2200        |
| Grandmaster 👑   | 20          | 24    | 5000 ms   | ~2600        |

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
- [x] 8 difficulty levels (Beginner → Grandmaster)
- [x] ELO rating and player profile
- [x] Game history with replay
- [x] Hot-seat (two players on one device)
- [x] Online PvP with invite codes (beta — sync on click)
- [ ] Live online PvP with pub/sub push notifications
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


</details>

<details>
<summary><strong>📖 Русский</strong></summary>

# Шахматный Telegram Бот

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react)](https://react.dev/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=flat-square&logo=telegram)](https://telegram.org/)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/chess)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

[English](#-description) • [Русский](#-описание)

</div>


<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/chess)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

[English](README_EN.md) • Русский

</div>

Полноценный Telegram-бот для игры в шахматы против AI на базе **Stockfish**. Полностью кнопочный интерфейс прямо внутри чата — доска как сетка inline-кнопок, без необходимости запускать WebApp. Также включён React WebApp как опциональный режим.


---

## Возможности

- **Полностью кнопочное управление**: единственная команда — `/start`, всё остальное через клавиатуры
- **Три режима игры**:
  - 🤖 **Против Stockfish** — 8 уровней сложности от Новичка до Гроссмейстера
  - 👥 **Hot-seat** — двое на одном устройстве, доска всегда показывается с позиции белых
  - 🌐 **Онлайн PvP** — играйте с другом по 6-значному коду приглашения (beta)
- **Иконки фигур для обоих цветов**: белые `♔♕♖♗♘♙`, чёрные `♚♛♜♝♞♟`
- **Доска как сетка inline-кнопок 8×8** без подписей рядов/файлов
- **Подсветка ходов**: 🟦 выбранная фигура · 🟢 возможный ход · 🟥 возможное взятие
- **Двухкликовый ход**: фигура → клетка назначения, автопромоушн пешки в ферзя
- **Стабильное обновление доски** — устойчивый рендер, ошибки `message is not modified` подавляются
- **Профиль игрока**: ELO-рейтинг (старт 1200, K = 32), пиковый ELO, винрейт, разбивка по уровням
- **История партий** — все сыгранные партии записываются в Redis с настройками, временем (МСК, UTC+3) и полным списком ходов; доступ из профиля
- Подсказка лучшего хода и оценка позиции (REST)
- Аутентификация через Telegram `initData` (HMAC-SHA256) — для WebApp
- WebSocket-синхронизация позиции — для WebApp
- Backend authoritative — все ходы валидируются на сервере
- Rate limiting (30 запросов/мин на пользователя)
- Полный Docker-стек: backend / frontend / redis / nginx

---

## Скриншот интерфейса бота

```
   ┌─────────────────────────────────┐
   │   ♔ Партия началась             │
   │   🎯 Уровень: Эксперт           │
   │   ♔ Вы играете: белые           │
   ├─────────────────────────────────┤
   │  ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜         │  ← чёрные фигуры
   │  ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟         │
   │  ⬜ ⬛ ⬜ ⬛ ⬜ ⬛ ⬜ ⬛           │  ← пустые клетки в цвет
   │  ⬛ ⬜ ⬛ ⬜ ⬛ ⬜ ⬛ ⬜           │
   │  ⬜ ⬛ ⬜ ⬛ 🟦 ⬛ ⬜ ⬛           │  ← подсветка выбранной
   │  ⬛ ⬜ ⬛ ⬜ 🟢 ⬜ ⬛ ⬜           │  ← возможный ход
   │  P  P  P  P  ⬜ P  P  P          │
   │  R  N  B  Q  K  B  N  R          │  ← белые фигуры (FEN)
   ├─────────────────────────────────┤
   │  🛑 Остановить игру             │
   └─────────────────────────────────┘
```

Белые фигуры обозначены буквами `K Q R B N P` (всегда видны на любой теме), чёрные — заполненными unicode-символами `♚ ♛ ♜ ♝ ♞ ♟`.

---

## Стек

### Backend
- Python 3.12, FastAPI, Uvicorn
- python-chess (chess engine API)
- Stockfish (серверный, пул воркеров)
- aiogram 3 (Telegram Bot API)
- Redis 7 (game sessions, статистика, история, rate limiting)
- PyJWT, Pydantic v2

### Frontend (опциональный WebApp)
- React 18, TypeScript 5, Vite 5
- react-chessboard, chess.js
- Zustand
- TailwindCSS
- Telegram WebApp SDK

### Infrastructure
- Docker Compose
- Nginx (reverse proxy для REST + WebSocket)

---

## Архитектура

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

## Кнопочный интерфейс

### Главное меню
- `♟️ Играть` · `👤 Профиль`
- `❓ Помощь`

### Выбор сложности
- `1️⃣ Лёгкий` · `2️⃣ Средний`
- `3️⃣ Сложный` · `4️⃣ Эксперт`
- `⬅️ Назад`

### Выбор цвета
- `⚪ Белые` · `⚫ Чёрные`
- `🎲 Случайно`
- `⬅️ Назад`

### В игре
- Доска как inline-сетка 8×8 (тап на фигуру → тап на клетку)
- `🛑 Остановить игру` — снизу под полем ввода

### Профиль
- ELO, рекорд, статистика, разбивка по уровням
- `📜 История игр` — список последних 10 партий с возможностью открыть детали (ходы, время, ELO до/после)
- `🗑 Сбросить статистику`
- `⬅️ Назад`

---

## Структура репозитория

```
.
├── backend/                     # FastAPI приложение
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

## Быстрый старт

### 1. Создайте Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather), команда `/newbot`
2. Сохраните полученный `TELEGRAM_BOT_TOKEN`
3. (Опционально) Настройте WebApp через `/setdomain` или `/newapp`, укажите публичный URL вашего деплоя

### 2. Клонируйте репозиторий

```bash
git clone https://github.com/Mukller/chess.git
cd chess
```

### 3. Настройте окружение

```bash
cp .env.example .env
# Откройте .env и подставьте:
# TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_WEBAPP_URL,
# APP_SECRET_KEY (минимум 32 случайных символа)
```

### 4. Запустите стек

```bash
docker compose up -d --build
```

Сервисы:
- `nginx` — порт `80` (frontend + REST + WS)
- `api` — внутренний, порт `8000`
- `frontend` — внутренний, порт `80`
- `redis` — внутренний, порт `6379`

После старта откройте бота в Telegram и отправьте `/start`. Дальше всё через кнопки.

### 5. Production-чеклист

- Поставьте Nginx за HTTPS-терминатором (Caddy / Traefik / Let's Encrypt)
- Установите `APP_ENV=production` — выключит Swagger UI
- Замените `APP_SECRET_KEY` на длинный случайный
- Настройте Prometheus/Grafana/Sentry (см. [RELEASE_INFO.md](RELEASE_INFO.md))

---

## ELO-система

| Параметр                  | Значение                     |
| ------------------------- | ---------------------------- |
| Стартовый рейтинг         | 1200                         |
| K-фактор                  | 32                           |
| ELO противника (Новичок)        | 500                    |
| ELO противника (Лёгкий)         | 800                    |
| ELO противника (Простой)        | 1100                   |
| ELO противника (Средний)        | 1400                   |
| ELO противника (Продвинутый)    | 1700                   |
| ELO противника (Сложный)        | 1900                   |
| ELO противника (Эксперт)        | 2200                   |
| ELO противника (Гроссмейстер)   | 2600                   |
| Учёт прерванной партии    | как поражение (`score = 0`) |

Формула: `delta = K * (actual - expected)`, где `expected = 1 / (1 + 10^((opp_elo - my_elo) / 400))`.

---

## REST API

Все эндпоинты требуют `Authorization: Bearer <jwt>` (кроме `/api/auth/telegram`).

| Метод | Путь                          | Описание                                  |
| ----- | ----------------------------- | ----------------------------------------- |
| POST  | `/api/auth/telegram`          | Обмен Telegram initData на access token   |
| POST  | `/api/game/start`             | Создать новую партию                      |
| GET   | `/api/game/{game_id}`         | Получить текущее состояние партии         |
| POST  | `/api/game/{game_id}/move`    | Сделать ход (UCI: `e2e4`, `e7e8q`)        |
| POST  | `/api/game/{game_id}/hint`    | Подсказка лучшего хода + оценка позиции   |
| POST  | `/api/game/{game_id}/undo`    | Откатить последнюю пару ходов             |
| POST  | `/api/game/{game_id}/resign`  | Сдаться                                   |
| GET   | `/health`                     | Health-check (Redis + engine + bot)       |

### WebSocket

`ws://host/ws/game/{game_id}?token=<jwt>`

Клиент шлёт: `{ "type": "move", "move": "e2e4" }`, `{ "type": "resign" }`, `{ "type": "ping" }`.

Сервер шлёт:
- `{ "type": "snapshot", "state": {...} }` — при подключении
- `{ "type": "position", "state": {...}, "player_move": "e2e4", "engine_move": {...} }`
- `{ "type": "game_over", "result": "1-0", "status": "checkmate" }`
- `{ "type": "error", "detail": "..." }`

---

## Уровни сложности Stockfish

| Уровень        | Skill Level | Глубина | Время хода | ELO противника |
| -------------- | ----------- | ------- | ---------- | -------------- |
| Новичок 🐣     | 0           | 2       | 80 ms      | ~500           |
| Лёгкий         | 3           | 4       | 150 ms     | ~800           |
| Простой        | 6           | 6       | 250 ms     | ~1100          |
| Средний        | 10          | 8       | 400 ms     | ~1400          |
| Продвинутый    | 14          | 11      | 700 ms     | ~1700          |
| Сложный        | 17          | 14      | 1200 ms    | ~1900          |
| Эксперт        | 20          | 18      | 2500 ms    | ~2200          |
| Гроссмейстер 👑| 20          | 24      | 5000 ms    | ~2600          |

Конфигурация в [backend/app/engine/config.py](backend/app/engine/config.py).

---

## Хранение данных

| Ключ Redis                   | TTL       | Содержимое                                    |
| ---------------------------- | --------- | --------------------------------------------- |
| `game:{id}`                  | 24 ч      | Активная партия (FEN, ходы, статус)           |
| `user:{id}:games`            | 24 ч      | Индекс активных партий пользователя           |
| `user:{id}:stats`            | 5 лет     | ELO, винрейт, разбивка по сложности           |
| `user:{id}:history`          | 5 лет     | Индекс завершённых партий (sorted set)        |
| `game_history:{id}`          | 5 лет     | Запись завершённой партии (полный лог ходов)  |
| `rl:{user}:{window}`         | 60 с      | Скользящее окно для rate limiting             |

Запись истории включает: настройки (сложность, цвет), время начала/конца в **МСК (UTC+3)**, полный список ходов в UCI, финальный FEN, ELO до и после, результат.

---

## Локальная разработка

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Установите stockfish: apt-get install stockfish или https://stockfishchess.org/
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# открой http://localhost:3000
```

Для тестирования вне Telegram WebApp авторизация работать не будет (нет валидного `initData`). Telegram-бот можно тестировать напрямую в чате через `/start`.

---

## Безопасность

- Telegram initData валидируется по HMAC-SHA256 (см. [backend/app/auth/telegram.py](backend/app/auth/telegram.py))
- Все ходы валидируются на сервере через python-chess — клиент только отправляет UCI
- JWT с TTL (по умолчанию 24 часа)
- WebSocket требует токен в query string
- Redis-based rate limiting (sliding window) — 30 req/мин на пользователя
- CSP и `X-Frame-Options` настроены для встраивания в Telegram

---

## Roadmap

- [x] Кнопочный UI без команд
- [x] 8 уровней сложности (Новичок → Гроссмейстер)
- [x] ELO рейтинг и профиль
- [x] История партий с пересмотром
- [x] Hot-seat (двое на одном устройстве)
- [x] Онлайн PvP с инвайт-кодами (beta — синхронизация по клику)
- [ ] Live онлайн PvP с pub/sub push-уведомлениями
- [ ] PGN экспорт партий
- [ ] Анализ сыгранных партий с движком
- [ ] Турниры
- [ ] Puzzle / Opening trainer

Подробнее: [CHANGELOG.md](CHANGELOG.md) · [RELEASE_INFO.md](RELEASE_INFO.md)

---

## Вклад

PR и issues приветствуются! См. [CONTRIBUTING.md](CONTRIBUTING.md) и [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Лицензия

MIT — см. [LICENSE.md](LICENSE.md).

---

## Контакты

- GitHub: [@Mukller](https://github.com/Mukller)
- Issues: [github.com/Mukller/chess/issues](https://github.com/Mukller/chess/issues)

</details>
