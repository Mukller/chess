# Backend Development Guide

FastAPI-based REST API and Telegram bot for the Chess application.

## Overview

The backend provides:
- **REST API** for game management, user stats, and move suggestions
- **Telegram Bot** using aiogram with button-based UI and WebApp integration
- **Chess Engine** using Stockfish with difficulty-based skill levels
- **Storage** using Redis for games, stats, and rate limiting
- **Authentication** via Telegram initData verification (HMAC-SHA256)
- **WebSocket** for real-time board synchronization with the React frontend

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application, lifespan, middleware
│   ├── config.py               # Settings from environment variables
│   ├── dependencies.py         # Dependency injection (auth, current_user)
│   │
│   ├── api/                    # REST API endpoints
│   │   ├── router.py           # Main router combining all routes
│   │   ├── auth.py             # POST /api/auth/telegram
│   │   ├── game.py             # /api/game/* endpoints
│   │   ├── user.py             # /api/user/* endpoints
│   │   ├── history.py          # /api/history/* endpoints
│   │   ├── online.py           # /api/online/* endpoints (beta)
│   │   └── ws.py               # WebSocket handler /ws/game/{game_id}
│   │
│   ├── bot/                    # Telegram bot handlers
│   │   ├── setup.py            # Bot initialization
│   │   ├── handlers.py         # Command and callback handlers
│   │   ├── states.py           # FSM states (selecting_difficulty, etc.)
│   │   └── keyboards.py        # Inline buttons and reply keyboards
│   │
│   ├── game/                   # Game logic
│   │   ├── models.py           # GameState, Difficulty, Color, GameStatus
│   │   ├── service.py          # GameService (create, move, resign)
│   │   ├── stats.py            # StatsService (ELO rating, user stats)
│   │   ├── history.py          # HistoryService (game records)
│   │   ├── online.py           # OnlineService (PvP games - beta)
│   │   └── config.py           # Difficulty profiles (skill, depth, move_time)
│   │
│   ├── engine/                 # Stockfish engine integration
│   │   ├── stockfish.py        # Stockfish engine wrapper (UCI protocol)
│   │   ├── pool.py             # EnginePool (manage multiple workers)
│   │   ├── config.py           # DifficultyProfile configuration
│   │   └── moves.py            # Move suggestions, evaluation, hints
│   │
│   ├── storage/                # Data persistence
│   │   ├── redis_client.py     # Redis connection (singleton)
│   │   ├── game_store.py       # Game state serialization
│   │   ├── stats_store.py      # User stats storage
│   │   └── rate_limit.py       # Rate limiting (sliding window)
│   │
│   ├── middleware/             # Custom middleware
│   │   ├── auth.py             # JWT token extraction
│   │   └── rate_limit.py       # Rate limiting middleware
│   │
│   └── telegram/               # Telegram integration
│       ├── auth.py             # initData verification
│       └── types.py            # TypedDict for Telegram data
│
├── tests/
│   ├── test_game.py            # Game service tests
│   ├── test_stats.py           # Stats calculation tests
│   ├── test_engine.py          # Engine pool tests
│   └── test_auth.py            # Authentication tests
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── Dockerfile                  # Container image
└── README.md                   # This file
```

---

## Key Services

### GameService

Manages game lifecycle: create, retrieve, update, resign.

```python
from app.game.service import GameService
from app.game.models import Difficulty, Color

service = GameService()

# Start game
game = await service.start(
    user_id=123,
    difficulty=Difficulty.MEDIUM,
    color=Color.WHITE
)

# Make move
result = await service.make_move(
    game_id=game.game_id,
    user_id=123,
    move="e2e4"  # UCI format
)

# Get game
game = await service.get(game.game_id, user_id=123)

# Resign
game = await service.resign(game.game_id, user_id=123)
```

### StatsService

Calculates ELO rating and user statistics.

```python
from app.game.stats import StatsService

service = StatsService()

# Get user stats
stats = await service.get(user_id=123)
# Returns: UserStats(elo=1347, peak_elo=1520, games_played=42, ...)

# Record game result
update = await service.record_result(
    user_id=123,
    difficulty=Difficulty.HARD,
    user_score=1.0  # 1.0 win, 0.5 draw, 0.0 loss
)
# Returns: EloUpdate(elo_before=1347, elo_after=1367, delta=20, ...)

# Reset stats
stats = await service.reset(user_id=123)
```

**ELO Calculation**:
- Initial ELO: 1200
- K-factor: 32
- Formula: `expected = 1 / (1 + 10^((opp_elo - player_elo) / 400))`
- Change: `delta = round(K_factor * (score - expected))`

### EnginePool

Manages Stockfish worker processes for parallel move computation.

```python
from app.engine.pool import EnginePool
from app.game.config import profile_for
from app.game.models import Difficulty

pool = EnginePool()

# Get best move
profile = profile_for(Difficulty.HARD)
move = await pool.get_best_move(
    fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    profile=profile  # DifficultyProfile(skill_level=17, depth=14, move_time_ms=1200)
)
# Returns: "c7c5" (best move in UCI format)

# Get evaluation
evaluation = await pool.evaluate(fen=fen)
# Returns: {"score": 25, "mate_in": null}

# Suggestion (best move + alternatives)
suggestion = await pool.get_suggestion(fen=fen, depth=10)
# Returns: {"best_move": "e2e4", "alternatives": [...]}
```

### RedisClient

Singleton Redis connection for storing games, stats, and rate limiting.

```python
from app.storage.redis_client import RedisClient

redis = RedisClient.instance()

# Game state storage (TTL: 1 day)
await redis.set(f"game:{game_id}", json.dumps(game_state), ex=86400)

# User stats (TTL: 5 years)
await redis.set(f"user:{user_id}:stats", json.dumps(stats), ex=157680000)

# Rate limiting (sliding window, 60s)
await redis.zadd(f"rate_limit:{user_id}", {request_id: timestamp})
```

---

## API Endpoints

See [API_REFERENCE.md](../API_REFERENCE.md) for complete documentation.

**Key Endpoints**:
- `POST /api/auth/telegram` — Exchange initData for JWT
- `POST /api/game/start` — Start new AI game
- `POST /api/game/{game_id}/move` — Make a move
- `GET /api/user/stats` — Get user ELO and stats
- `GET /api/history/list` — Get game history
- `POST /api/online/create` — Create online game
- `WS /ws/game/{game_id}` — Real-time board sync

---

## Telegram Bot

The bot uses aiogram 3 with Finite State Machine (FSM) for conversation flow.

### States

```
/start
  ↓
Main Menu (BTN_PLAY, BTN_PROFILE, BTN_HELP)
  ↓
[Button Click] → selecting_difficulty
  ↓
[Difficulty Selected] → selecting_color
  ↓
[Color Selected] → game_in_progress
  ↓
[Game Finished] → Back to Main Menu
```

### Handlers

```python
# backend/app/bot/handlers.py
@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext):
    # Show main menu
    
@router.callback_query(F.data == "play")
async def on_play_click(query: CallbackQuery, state: FSMContext):
    # Show difficulty selection
    await state.set_state(GameState.selecting_difficulty)

@router.callback_query(GameState.selecting_difficulty)
async def on_difficulty_selected(query: CallbackQuery, state: FSMContext):
    # Save difficulty and show color selection
    difficulty = ...
    await state.update_data(difficulty=difficulty)
    await state.set_state(GameState.selecting_color)
```

### Inline Buttons

Chess board rendered as 8×8 grid of inline buttons:

```python
PIECE_GLYPHS = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",  # white
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",  # black
}

EMPTY_LIGHT = "·"     # Light square
EMPTY_DARK = " "      # Dark square
HL_SELECTED = "🟦"    # Selected piece
HL_MOVE_LIGHT = "🟢"  # Possible move (light)
HL_CAPTURE = "🟥"     # Possible capture
```

---

## Authentication

### Telegram initData Verification

```python
from app.telegram.auth import verify_init_data

init_data = "query_id=...&user={...}&..."
is_valid = verify_init_data(init_data, bot_token)

if is_valid:
    user_data = parse_init_data(init_data)
    jwt_token = create_jwt_token(user_id=user_data["id"])
```

### JWT Token

```python
from app.dependencies import get_current_user

# In route handler:
@router.get("/api/user/stats")
async def get_stats(current_user: CurrentUser = Depends(get_current_user)):
    # current_user contains user_id, username, first_name
    return await stats_service.get(current_user.user_id)
```

---

## Configuration

### Environment Variables

See [.env.example](.env.example) for all variables.

**Key variables**:
- `APP_ENV` — development or production
- `TELEGRAM_BOT_TOKEN` — Bot token from @BotFather
- `REDIS_URL` — Redis connection string (redis://redis:6379/0)
- `STOCKFISH_PATH` — Path to stockfish binary (/usr/games/stockfish)
- `STOCKFISH_WORKERS` — Number of engine processes (4 recommended)
- `APP_SECRET_KEY` — Secret for JWT signing (minimum 32 chars)

### Difficulty Profiles

```python
# backend/app/engine/config.py
DIFFICULTY_PROFILES = {
    Difficulty.BEGINNER: DifficultyProfile(skill_level=0,  depth=2,  move_time_ms=80),
    Difficulty.EASY:     DifficultyProfile(skill_level=3,  depth=4,  move_time_ms=150),
    Difficulty.CASUAL:   DifficultyProfile(skill_level=6,  depth=6,  move_time_ms=250),
    Difficulty.MEDIUM:   DifficultyProfile(skill_level=10, depth=8,  move_time_ms=400),
    Difficulty.ADVANCED: DifficultyProfile(skill_level=14, depth=11, move_time_ms=700),
    Difficulty.HARD:     DifficultyProfile(skill_level=17, depth=14, move_time_ms=1200),
    Difficulty.EXPERT:   DifficultyProfile(skill_level=20, depth=18, move_time_ms=2500),
    Difficulty.MASTER:   DifficultyProfile(skill_level=20, depth=24, move_time_ms=5000),
}
```

---

## Development

### Running Locally

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Update values

# Ensure Redis is running
redis-cli ping  # Should return PONG

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/game/test_service.py::test_create_game

# Watch mode
pytest-watch tests/
```

### Type Checking

```bash
mypy app/ --pretty
```

### Linting & Formatting

```bash
ruff check app/         # Check style
ruff check app/ --fix   # Fix auto-fixable issues
ruff format app/        # Format code
```

---

## Common Tasks

### Adding a New Endpoint

1. Create handler in `api/your_feature.py`
2. Add to router in `api/router.py`
3. Update [API_REFERENCE.md](../API_REFERENCE.md)
4. Add tests in `tests/test_api_your_feature.py`

Example:

```python
# app/api/hint.py
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["hint"])

@router.get("/game/{game_id}/hint")
async def get_hint(
    game_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get hint (best move) for current position."""
    game = await game_service.get(game_id, current_user.user_id)
    suggestion = await engine_pool.get_suggestion(game.fen)
    return {"best_move": suggestion["best_move"]}
```

### Adding a New Handler

1. Create handler in `bot/handlers.py`
2. Register with router
3. Add FSM state if needed in `bot/states.py`
4. Create keyboard in `bot/keyboards.py`

Example:

```python
# bot/handlers.py
@router.callback_query(F.data == "profile")
async def on_profile_click(query: CallbackQuery, current_user: CurrentUser):
    """Show user profile with ELO and stats."""
    stats = await stats_service.get(current_user.user_id)
    text = f"""
    👤 <b>Profile</b>
    
    🎯 ELO: {stats.elo}
    📊 Games: {stats.games_played}
    ✅ Wins: {stats.wins}
    ❌ Losses: {stats.losses}
    """
    await query.answer()
    await query.message.edit_text(text, reply_markup=main_keyboard())
```

### Debugging

```bash
# Set log level
export APP_LOG_LEVEL=DEBUG

# Run with debug output
uvicorn app.main:app --reload --log-level debug

# View logs in Docker
docker compose logs -f api
docker compose logs api | grep ERROR
```

---

## Performance Tuning

### Stockfish Workers

Adjust based on CPU cores:

```bash
# Get CPU count
nproc  # Linux/Mac
# Set in .env: STOCKFISH_WORKERS = (nproc / 2)
# Example: 8-core → STOCKFISH_WORKERS=4
```

### Redis Connection Pool

Increase for high concurrency:

```python
# app/storage/redis_client.py
redis = aioredis.from_url(
    url,
    encoding="utf-8",
    max_connections=50  # Adjust based on load
)
```

### Rate Limiting

Adjust per-minute limit:

```bash
# .env
RATE_LIMIT_PER_MINUTE=30  # Default: 30 req/min per user
```

---

## Security Notes

- ✅ Validate moves with python-chess (authoritative check)
- ✅ Verify JWT tokens before accessing user data
- ✅ Use HTTPS in production
- ✅ Rate limit API requests per user
- ❌ Never trust client-provided moves without validation
- ❌ Don't expose internal errors to clients
- ❌ Don't log sensitive data (tokens, passwords)

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "engine_ready": true, "bot_configured": true}
```

### Database

```bash
# Redis stats
docker exec chess_redis redis-cli info stats

# Game keys
docker exec chess_redis redis-cli KEYS "game:*"

# Memory usage
docker exec chess_redis redis-cli info memory
```

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [aiogram Documentation](https://docs.aiogram.dev/)
- [python-chess Documentation](https://python-chess.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Stockfish UCI Protocol](https://chess.com/terms/chess-engine)

---

## Next Steps

- See [../QUICK_START.md](../QUICK_START.md) for local setup
- See [../API_REFERENCE.md](../API_REFERENCE.md) for API docs
- See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

Happy coding! 🚀
