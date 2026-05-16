# Telegram Chess Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)

Полноценный Telegram-бот с **WebApp** интерфейсом для игры в шахматы против AI на базе **Stockfish**.

> 🇬🇧 English version: [README_EN.md](README_EN.md)

---

## Возможности

- Игра против Stockfish (3 уровня сложности: лёгкий / средний / сложный)
- Полноценная шахматная доска: drag-and-drop, подсветка возможных ходов, отображение шаха
- Подсказка лучшего хода с оценкой позиции
- Откат хода (Undo), сдача (Resign), новая партия (New Game)
- Аутентификация через Telegram `initData` (HMAC-SHA256, серверная валидация)
- WebSocket-синхронизация позиции в реальном времени
- Backend authoritative — все ходы валидируются на сервере
- Сессии игры в Redis (TTL 24 часа по умолчанию)
- Rate limiting (30 запросов/минуту на пользователя)
- Полный Docker-стек: backend / frontend / redis / nginx

---

## Стек

### Backend
- Python 3.12, FastAPI, Uvicorn
- python-chess (chess engine API)
- Stockfish (серверный, пул воркеров)
- aiogram 3 (Telegram Bot API)
- Redis 7 (game sessions, rate limiting)
- PyJWT, Pydantic v2

### Frontend
- React 18, TypeScript 5, Vite 5
- react-chessboard, chess.js
- Zustand (state management)
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
           │ /play, /start                │ HTTPS + WSS
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
       ┌──────────────────────────┐
       │      GameService          │
       │  (python-chess, repo)     │
       └──────┬──────────┬─────────┘
              │          │
              ▼          ▼
        ┌─────────┐  ┌─────────────────┐
        │  Redis  │  │   EnginePool    │
        └─────────┘  │ N Stockfish proc│
                     └─────────────────┘
```

---

## Структура репозитория

```
.
├── backend/                     # FastAPI приложение
│   ├── app/
│   │   ├── auth/                # Telegram initData + JWT
│   │   ├── bot/                 # aiogram bot + handlers
│   │   ├── engine/              # Stockfish pool
│   │   ├── game/                # GameService, REST routes, models
│   │   ├── middleware/          # Rate limiting
│   │   ├── storage/             # Redis client
│   │   ├── ws/                  # WebSocket gateway
│   │   ├── config.py
│   │   └── main.py
│   ├── Dockerfile               # Stockfish + Python
│   └── requirements.txt
├── frontend/                    # React + Vite WebApp
│   ├── src/
│   │   ├── api/                 # REST + WS клиент
│   │   ├── components/          # Board, MoveList, HintPanel, …
│   │   ├── hooks/               # useTelegram, useGameSocket
│   │   ├── pages/               # HomePage, GamePage
│   │   ├── store/               # Zustand stores
│   │   └── types/
│   ├── Dockerfile               # multi-stage: build + nginx
│   └── package.json
├── nginx/
│   └── nginx.conf               # reverse proxy
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
3. Настройте WebApp через `/setdomain` или `/newapp`, укажите публичный URL вашего деплоя

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

После старта откройте бота в Telegram, отправьте `/play` и нажмите кнопку «Играть».

### 5. Production-чеклист

- Поставьте Nginx за HTTPS-терминатором (Caddy / Traefik / Let's Encrypt)
- Установите `APP_ENV=production` — выключит Swagger UI
- Замените `APP_SECRET_KEY` на длинный случайный
- Настройте Prometheus/Grafana/Sentry (см. [RELEASE_INFO.md](RELEASE_INFO.md))

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

| Уровень   | Skill Level | Глубина | Время хода |
| --------- | ----------- | ------- | ---------- |
| Easy      | 2           | 4       | 100 ms     |
| Medium    | 8           | 8       | 300 ms     |
| Hard      | 18          | 14      | 1200 ms    |

Конфигурация в [backend/app/engine/config.py](backend/app/engine/config.py).

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

Для тестирования вне Telegram WebApp авторизация работать не будет (нет валидного `initData`).

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

- [ ] PvP (игрок vs игрок)
- [ ] ELO рейтинг и история партий (PostgreSQL)
- [ ] PGN экспорт партий
- [ ] Анализ сыгранных партий
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
