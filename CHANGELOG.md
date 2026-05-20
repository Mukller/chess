# Changelog

Все значимые изменения проекта документируются здесь. Формат основан на
[Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии следуют
[Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Planned
- PvP режим
- Экспорт PGN
- Анализ сыгранных партий движком
- Турниры / Puzzle / Opening trainer

---

## [1.1.0] — 2026-05-21

Полный редизайн Telegram-бота: кнопочный интерфейс, профиль с ELO, история партий.

### Added
- **Кнопочный UI**: единственная команда — `/start`, всё остальное через ReplyKeyboard и inline-кнопки
- **Доска как сетка inline-кнопок 8×8** с цветными клетками (`⬜`/`⬛`), без подписей a-h / 1-8
- **Подсветка ходов**: 🟦 выбранная фигура · 🟢/🟩 возможный ход · 🟥 возможное взятие
- **Двухкликовый ход** (фигура → клетка), автопромоушн пешки в ферзя
- **Авто-переворот доски** при игре чёрными
- **Уровень `Эксперт`** — Stockfish skill=20, depth=22, time=3000ms (ELO ~2400)
- **Профиль игрока** (`👤 Профиль`) с ELO-рейтингом, винрейтом, разбивкой по сложности
- **ELO-система**: старт 1200, K=32, формула классического Elo с зависимостью от уровня противника
- **История партий** (`📜 История игр`) — последние 10 партий с настройками, временем (МСК, UTC+3) и полным списком ходов
- **Хранение завершённых партий** в Redis (TTL 5 лет, до 200 записей на пользователя)
- **Кнопка `🛑 Остановить игру`** в ReplyKeyboard под полем ввода (не в inline-доске)

### Changed
- Рендер фигур: белые — буквами FEN (`K Q R B N P`), чёрные — заполненными unicode (`♚ ♛ ♜ ♝ ♞ ♟`). Гарантированно видны на любой теме
- `Difficulty` enum пополнен `EXPERT`
- `TelegramBot` принимает `engine_pool` и инжектит его в `Dispatcher` workflow data — handlers теперь получают пул как DI-параметр
- README.md и README_EN.md полностью переписаны под новый дизайн

### Fixed
- `engine_pool=None` в bot-handlers — компьютер не отвечал на ход. Теперь пул реально подключён
- `GameService.get()` вызывался без `user_id` — поднимался TypeError

---

## [1.0.0] — 2026-05-16

Первый MVP-релиз: полностью рабочий Telegram-бот с WebApp интерфейсом и серверным Stockfish.

### Added — Phase 1 · Infrastructure
- Docker Compose со всеми сервисами: `redis`, `api`, `frontend`, `nginx`
- Nginx как reverse proxy: REST `/api/`, WebSocket `/ws/`, статика SPA
- `.env.example` со всеми параметрами окружения
- Healthchecks для `redis` и `api`

### Added — Phase 2 · Backend foundation
- FastAPI приложение с lifespan-управляемым Redis-пулом и graceful shutdown
- Pydantic-settings: все настройки через ENV, кешируются через `lru_cache`
- Telegram WebApp `initData` валидация по HMAC-SHA256
- JWT issuance (PyJWT) с TTL и dependency для bearer-аутентификации
- Эндпоинт `POST /api/auth/telegram` — обмен initData на access token
- Sliding-window rate limiter в Redis (sorted set), 30 req/мин на пользователя
- `Dockerfile` для backend с предустановленным `stockfish`

### Added — Phase 3 · Chess logic
- Dataclass `GameState` со статусами (`active`/`checkmate`/`stalemate`/`draw`/`resigned`)
- Redis repository с per-user индексом партий, сортированных по последнему ходу
- `GameService` (authoritative): валидация ходов через python-chess, определение терминальных состояний
- REST эндпоинты: `start`, `get`, `move`, `hint`, `undo`, `resign`
- Корректный `undo`: откатывает пару ходов (ход движка + ход пользователя)

### Added — Phase 4 · Stockfish + WebSocket + Telegram bot
- `EnginePool`: N персистентных Stockfish-воркеров, диспатч через `asyncio.Queue`
- Профили сложности (Easy/Medium/Hard) с конфигурируемым `Skill Level`, глубиной и временем
- WebSocket `/ws/game/{game_id}?token=...` с broadcast через `ConnectionManager`
- Сообщения WS: `snapshot`, `position`, `game_over`, `error`, `pong`; клиент шлёт `move`/`resign`/`ping`
- Aiogram 3 бот с `/start`, `/play`, `/help` и кнопкой `WebAppInfo`
- Polling бота как `asyncio.Task` в lifespan приложения

### Added — Phase 5 · Frontend (React WebApp)
- Vite + React 18 + TypeScript + TailwindCSS toolchain
- `react-chessboard` с подсветкой последнего хода, шаха и подсказки
- Клиент chess.js используется только для SAN-рендеринга (backend authoritative)
- Zustand-сторы: `useSessionStore`, `useGameStore`
- Telegram WebApp SDK: initData login + темизация через CSS-переменные
- WebSocket клиент с auto-reconnect (exponential backoff) и keepalive ping
- HomePage — выбор сложности и цвета; GamePage — игровая доска со всеми контролами
- Hint / Undo / Resign / New Game UI
- Multi-stage Dockerfile (build + nginx)

### Added — Phase 6 · Documentation
- README на русском и английском
- CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, RELEASE_INFO

### Security
- Backend authoritative для всех ходов и состояний партии
- HMAC-SHA256 верификация Telegram initData с проверкой `auth_date`
- JWT bearer для REST и WebSocket
- Per-user rate limiting через Redis
- `X-Frame-Options` и CSP настроены для встраивания в Telegram

---

## [0.0.1] — 2026-05-16

- Создан репозиторий, скелет проекта

[Unreleased]: https://github.com/Mukller/chess/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Mukller/chess/releases/tag/v1.0.0
[0.0.1]: https://github.com/Mukller/chess/releases/tag/v0.0.1
