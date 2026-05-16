# Release Info — v1.0.0

> Дата релиза: **2026-05-16**
> Кодовое имя: **First Move** ♟️
> Тег: [`v1.0.0`](https://github.com/Mukller/chess/releases/tag/v1.0.0)

Первый MVP-релиз Telegram Chess Bot. Полностью рабочий стек: React WebApp + FastAPI
backend + Stockfish engine pool + Redis + Nginx, собранный в Docker Compose.

---

## ✨ Highlights

- ♟️ **Играй прямо в Telegram** — нативный WebApp интерфейс с drag-and-drop доской
- 🤖 **Серверный Stockfish** с тремя уровнями (Easy / Medium / Hard)
- 🧠 **Подсказки** лучшего хода + оценка позиции
- 🔄 **WebSocket** реалтайм-синхронизация партии
- 🛡 **Server authoritative**: все ходы валидируются на бэке через python-chess
- 🔐 **Telegram initData** валидация (HMAC-SHA256) + JWT для последующих запросов
- 🚀 **Docker Compose**: `docker compose up -d --build` — и всё работает

---

## 📦 Что внутри

### Backend (Python 3.12 + FastAPI)
- `app/auth` — Telegram initData / JWT / Bearer-dependency
- `app/game` — `GameService`, REST routes, Redis repository
- `app/engine` — `EnginePool` с N персистентными Stockfish-процессами
- `app/ws` — WebSocket gateway + connection manager (broadcast по `game_id`)
- `app/bot` — aiogram 3 polling с `/start`, `/play`, `/help`
- `app/middleware/rate_limit.py` — sliding-window лимитер на Redis sorted sets

### Frontend (React 18 + TS + Vite)
- `src/api` — REST клиент, WebSocket клиент с auto-reconnect
- `src/components` — Board, MoveList, HintPanel, GameControls, DifficultySelector, ColorSelector
- `src/pages` — HomePage (выбор сложности/цвета), GamePage (партия)
- `src/store` — Zustand (`useSessionStore`, `useGameStore`)
- `src/hooks` — `useTelegram`, `useGameSocket`

### Infrastructure
- `docker-compose.yml` со всеми сервисами (`redis`, `api`, `frontend`, `nginx`)
- `nginx/nginx.conf` — reverse proxy для REST + WebSocket + статика
- `.env.example` со всеми параметрами

---

## 🎯 Performance targets (по ТЗ)

| Метрика                | Цель        | Что измеряет                              |
| ---------------------- | ----------- | ----------------------------------------- |
| API response (avg)     | < 100 ms    | `/api/game/move` без учёта engine         |
| Engine move (avg)      | < 1.5 s     | Stockfish best_move на медиум-сложности   |
| Concurrent games       | 100+        | Одновременных активных партий в Redis     |

EnginePool по умолчанию запускает 4 воркера — настраивается через
`STOCKFISH_WORKERS` в `.env`.

---

## 🚀 Установка и запуск

См. подробный гайд в [README.md](README.md#быстрый-старт) (RU) или
[README_EN.md](README_EN.md#quick-start) (EN). Кратко:

```bash
git clone https://github.com/Mukller/chess.git
cd chess
cp .env.example .env
# Заполнить TELEGRAM_BOT_TOKEN, TELEGRAM_WEBAPP_URL, APP_SECRET_KEY
docker compose up -d --build
```

---

## 🔒 Security notes

- Telegram `initData` валидируется по HMAC-SHA256 со сверкой `auth_date` и TTL
- Все ходы валидируются сервером через python-chess — клиент не может подменить позицию
- JWT bearer-токен с TTL (по умолчанию 24 часа)
- WebSocket требует токен в query string (`?token=`)
- Rate limiter — 30 запросов/минуту на пользователя через Redis sorted set
- `X-Frame-Options` и CSP настроены для встраивания только в `web.telegram.org`
- В production режиме (`APP_ENV=production`) выключаются Swagger UI и ReDoc

---

## 📊 Monitoring (рекомендации)

ТЗ упоминает рекомендуемые инструменты — они не входят в MVP, но интеграция готова:

- **Prometheus** — добавьте `prometheus-fastapi-instrumentator` (1 строка в `main.py`)
- **Grafana** — дашборды на основе Prometheus метрик
- **Sentry** — `sentry-sdk[fastapi]` для трекинга ошибок

---

## ⚠️ Known limitations

- Нет PostgreSQL — партии живут в Redis с TTL 24 часа (по ТЗ это MVP)
- Нет постоянной истории партий (только активная)
- Нет PvP — только vs AI
- Нет ELO рейтинга
- Бот работает через polling — для масштабирования рекомендуется webhook
- Stockfish — синглтон-процессы, нет распределённого engine-service (это есть в roadmap)

---

## 🛣 Roadmap до 1.1.0

- [ ] PostgreSQL persistence (история партий, ELO)
- [ ] PGN экспорт
- [ ] Webhook вместо polling для бота
- [ ] Prometheus метрики из коробки
- [ ] CI (lint + typecheck + build)
- [ ] Базовые pytest-тесты для `GameService` и `verify_init_data`

---

## 👥 Credits

- **Author**: [@Mukller](https://github.com/Mukller)
- **Engine**: [Stockfish](https://stockfishchess.org/) team
- **Libraries**: [python-chess](https://python-chess.readthedocs.io/), [react-chessboard](https://github.com/Clariity/react-chessboard), [chess.js](https://github.com/jhlywa/chess.js), [aiogram](https://aiogram.dev/)
- **Brewed with**: [Claude Code](https://claude.com/claude-code)

---

## 📄 License

MIT — см. [LICENSE.md](LICENSE.md). Stockfish — GPL-3.0 (см. секцию third-party).
