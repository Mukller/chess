# API Reference

Complete REST API documentation for the Telegram Chess Bot backend.

**Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)

**Authentication**: JWT Bearer token (except `/auth/telegram` endpoint)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Games](#games)
3. [Moves](#moves)
4. [User Profile](#user-profile)
5. [History](#history)
6. [Online Games](#online-games)
7. [WebSocket](#websocket)
8. [Health & Status](#health--status)

---

## Authentication

### Telegram WebApp Authentication

**Endpoint**: `POST /api/auth/telegram`

Exchange Telegram `initData` for JWT token.

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "init_data": "query_id=...&user={...}&..."
  }'
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 123456789,
  "username": "username"
}
```

**Error** (401):
```json
{
  "detail": "Invalid initData signature"
}
```

### Using Token

Include token in all subsequent requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/game/list
```

---

## Games

### Start New Game

**Endpoint**: `POST /api/game/start`

Start a new AI game against Stockfish.

**Request**:
```json
{
  "difficulty": "medium",
  "color": "white"
}
```

**Parameters**:
- `difficulty`: `beginner|easy|casual|medium|advanced|hard|expert|master`
- `color`: `white|black`

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "status": "active",
  "user_color": "white",
  "difficulty": "medium",
  "moves": [],
  "created_at": 1621234567
}
```

**Error** (400):
```json
{
  "detail": "Invalid difficulty level"
}
```

### Get Game State

**Endpoint**: `GET /api/game/{game_id}`

Retrieve current game state.

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "status": "active",
  "user_color": "white",
  "difficulty": "medium",
  "moves": ["e2e4"],
  "created_at": 1621234567,
  "updated_at": 1621234568
}
```

**Error** (404):
```json
{
  "detail": "Game not found"
}
```

### List Active Games

**Endpoint**: `GET /api/game/list`

Get all active games for the current user.

**Response** (200):
```json
{
  "games": [
    {
      "game_id": "uuid-1",
      "status": "active",
      "difficulty": "medium",
      "created_at": 1621234567
    },
    {
      "game_id": "uuid-2",
      "status": "checkmate",
      "difficulty": "hard",
      "created_at": 1621234500
    }
  ],
  "total": 2
}
```

---

## Moves

### Make a Move

**Endpoint**: `POST /api/game/{game_id}/move`

Submit a move in UCI format or algebraic notation.

**Request**:
```json
{
  "move": "e2e4"
}
```

**Alternative** (algebraic):
```json
{
  "move": "e4"
}
```

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "move": "e2e4",
  "user_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "engine_move": "c7c5",
  "engine_fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
  "status": "active",
  "result": null,
  "move_time_ms": 325
}
```

**Possible game statuses**:
- `active` — Game in progress
- `checkmate` — User won or lost
- `stalemate` — Draw
- `draw` — Draw (50-move rule, 3x repetition, insufficient material)
- `resigned` — Opponent resigned
- `abandoned` — Game abandoned

**Error** (400):
```json
{
  "detail": "Illegal move e5e6"
}
```

**Error** (409):
```json
{
  "detail": "Game already finished"
}
```

### Resign Game

**Endpoint**: `POST /api/game/{game_id}/resign`

Forfeit the current game.

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "status": "resigned",
  "result": "loss"
}
```

### Get Move Suggestions

**Endpoint**: `GET /api/game/{game_id}/suggest`

Get best move and position evaluation.

**Query Parameters**:
- `depth`: `1-24` (default: 10)

**Response** (200):
```json
{
  "best_move": "e2e4",
  "evaluation": {
    "score": 25,
    "mate_in": null
  },
  "alternatives": [
    {
      "move": "d2d4",
      "score": 20
    },
    {
      "move": "c2c4",
      "score": 18
    }
  ]
}
```

---

## User Profile

### Get User Stats

**Endpoint**: `GET /api/user/stats`

Retrieve user's ELO rating, win/loss record, and stats by difficulty.

**Response** (200):
```json
{
  "user_id": 123456789,
  "elo": 1347,
  "peak_elo": 1520,
  "games_played": 42,
  "wins": 18,
  "losses": 20,
  "draws": 4,
  "by_difficulty": {
    "beginner": {"played": 5, "wins": 5, "losses": 0, "draws": 0},
    "easy": {"played": 8, "wins": 6, "losses": 2, "draws": 0},
    "medium": {"played": 15, "wins": 4, "losses": 10, "draws": 1},
    "hard": {"played": 14, "wins": 3, "losses": 8, "draws": 3}
  }
}
```

### Reset Statistics

**Endpoint**: `POST /api/user/reset-stats`

Reset user statistics to initial state (ELO = 1200, all stats = 0).

**Response** (200):
```json
{
  "user_id": 123456789,
  "elo": 1200,
  "peak_elo": 1200,
  "games_played": 0,
  "wins": 0,
  "losses": 0,
  "draws": 0,
  "by_difficulty": {}
}
```

---

## History

### Get Game History

**Endpoint**: `GET /api/history/list`

Retrieve all completed games.

**Query Parameters**:
- `limit`: `1-100` (default: 20)
- `offset`: `0+` (default: 0)
- `difficulty`: Filter by difficulty (optional)

**Response** (200):
```json
{
  "games": [
    {
      "game_id": "uuid-1",
      "difficulty": "medium",
      "user_color": "white",
      "status": "checkmate",
      "result": "win",
      "moves_count": 42,
      "duration_seconds": 1245,
      "played_at": "2026-05-21T19:30:00+03:00",
      "moves": ["e2e4", "c7c5", ...]
    }
  ],
  "total": 157,
  "limit": 20,
  "offset": 0
}
```

### Get Game Details

**Endpoint**: `GET /api/history/{game_id}`

Get full details of a completed game.

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "difficulty": "hard",
  "user_color": "white",
  "status": "checkmate",
  "result": "win",
  "final_fen": "rnb1kbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3",
  "moves": ["e2e4", "c7c5", "g1f3", "d7d6"],
  "move_times_ms": [150, 325, 280, 410],
  "played_at": "2026-05-21T19:30:00+03:00",
  "duration_seconds": 1245
}
```

---

## Online Games

### Create Online Game

**Endpoint**: `POST /api/online/create`

Create a new online game and get invitation code.

**Request**:
```json
{
  "time_control": "10+5"
}
```

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "invite_code": "ABC123",
  "status": "waiting",
  "created_at": 1621234567,
  "expires_at": 1621238167
}
```

### Join Online Game

**Endpoint**: `POST /api/online/join`

Join an existing online game with invite code.

**Request**:
```json
{
  "invite_code": "ABC123"
}
```

**Response** (200):
```json
{
  "game_id": "uuid-here",
  "status": "in_progress",
  "opponent_id": 987654321,
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

**Error** (400):
```json
{
  "detail": "Invite code expired or invalid"
}
```

### List Online Games

**Endpoint**: `GET /api/online/list`

Get all online games for the current user.

**Response** (200):
```json
{
  "games": [
    {
      "game_id": "uuid-1",
      "opponent_id": 987654321,
      "status": "in_progress",
      "created_at": 1621234567
    }
  ],
  "total": 1
}
```

---

## WebSocket

### Connect to Game

**URL**: `ws://localhost:8000/ws/game/{game_id}?token=JWT_TOKEN`

Establish WebSocket connection for real-time board synchronization.

**Authentication**: Include JWT token in query parameter

**Message Format** (JSON):

**Incoming** (board update):
```json
{
  "type": "move",
  "move": "e2e4",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "status": "active"
}
```

**Incoming** (game end):
```json
{
  "type": "game_end",
  "status": "checkmate",
  "result": "win",
  "final_fen": "..."
}
```

**Outgoing** (user move):
```json
{
  "type": "move",
  "move": "e7e5"
}
```

**Connection Issues**:
- Token invalid → 401 Unauthorized
- Game not found → 404 Not Found
- Game finished → 410 Gone (connection closes)

---

## Health & Status

### Health Check

**Endpoint**: `GET /health`

System health and readiness status (no authentication required).

**Response** (200):
```json
{
  "status": "ok",
  "version": "1.2.0",
  "engine_ready": true,
  "bot_configured": true,
  "redis_connected": true
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "degraded",
  "version": "1.2.0",
  "engine_ready": false,
  "bot_configured": true,
  "redis_connected": false
}
```

---

## Error Handling

All errors follow standard HTTP status codes and include a detail message:

```json
{
  "detail": "Descriptive error message"
}
```

**Common Status Codes**:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Game created |
| 400 | Bad request | Invalid move |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not found | Game doesn't exist |
| 409 | Conflict | Game already finished |
| 429 | Rate limited | Too many requests |
| 500 | Server error | Engine crashed |
| 503 | Service unavailable | Redis down |

---

## Rate Limiting

All endpoints are rate limited: **30 requests per minute per user**.

**Headers**:
- `X-RateLimit-Limit: 30`
- `X-RateLimit-Remaining: 25`
- `X-RateLimit-Reset: 1621234627`

When limit exceeded: **429 Too Many Requests**

---

## OpenAPI/Swagger Documentation

Full interactive API documentation available at:

- **Development**: http://localhost:8000/docs
- **Production**: https://your-domain.com/docs

Alternative (ReDoc): `/redoc`

---

## Example: Complete Game Flow

```bash
# 1. Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{"init_data":"..."}' | jq -r '.access_token')

# 2. Start game
GAME=$(curl -s -X POST http://localhost:8000/api/game/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"difficulty":"medium","color":"white"}')

GAME_ID=$(echo $GAME | jq -r '.game_id')

# 3. Make move
curl -s -X POST http://localhost:8000/api/game/$GAME_ID/move \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"move":"e2e4"}'

# 4. Get stats
curl -s http://localhost:8000/api/user/stats \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Get history
curl -s http://localhost:8000/api/history/list \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Deployment Notes

- All endpoints support CORS (configurable via `CORS_ORIGINS` env var)
- Production requires HTTPS (enforce with security headers)
- API runs behind Nginx reverse proxy at `/api/` path
- WebSocket requires `Upgrade` header support (Nginx configured)
- Rate limiting uses Redis sliding-window algorithm

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Mukller/chess/issues)
- **Docs**: [README.md](README.md), [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Debug**: Enable `APP_LOG_LEVEL=DEBUG` in `.env`
