# Quick Start Guide

Get the Telegram Chess Bot running locally in minutes.

## Prerequisites

- Git
- Docker & Docker Compose (recommended) OR:
  - Python 3.12+
  - Node.js 18+
  - Redis 7+
  - Stockfish chess engine
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Option 1: Docker Compose (Easiest)

### 1. Clone & Setup

```bash
git clone https://github.com/Mukller/chess.git
cd chess

# Copy environment template
cp backend/.env.example backend/.env
```

### 2. Configure Environment

Edit `backend/.env`:

```bash
nano backend/.env
# Or use your editor:
# - TELEGRAM_BOT_TOKEN: Get from @BotFather (/newbot)
# - TELEGRAM_BOT_USERNAME: Your bot's username (without @)
# - TELEGRAM_WEBAPP_URL: http://localhost:3000 (for local dev)
# - APP_ENV: development
# - CORS_ORIGINS: ["http://localhost:3000","http://localhost"]
```

### 3. Start Services

```bash
docker compose up -d

# Verify all services are running
docker compose ps
# Expected: redis (Up), api (Up), frontend (Up), nginx (Up)

# Watch logs
docker compose logs -f api
```

### 4. Test Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Click "♟️ Играть с ботом"
5. Select difficulty and color

### 5. Access Frontend (Optional)

- **WebApp**: http://localhost/app
- **API Health**: http://localhost/health
- **API Docs**: http://localhost/docs (OpenAPI/Swagger)

---

## Option 2: Local Development (Python + Node.js)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure Redis is running on localhost:6379
redis-cli ping  # Should return "PONG"

# Copy and edit .env
cp .env.example .env
nano .env
# Adjust REDIS_URL if needed: redis://127.0.0.1:6379/0
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (runs on port 5173)
npm run dev
```

### Start API Server

```bash
cd backend

# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access in Browser

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Common Tasks

### Check Logs

```bash
# Docker Compose
docker compose logs -f api
docker compose logs -f redis
docker compose logs frontend

# Local development
# Terminal 1: Backend logs printed to console
# Terminal 2: Frontend logs (npm run dev)
```

### Verify Services

```bash
# Docker Compose
docker compose ps

# Health check
curl http://localhost:8000/health

# Redis
docker exec chess_redis redis-cli ping
# Or (local): redis-cli ping
```

### Test API Endpoints

```bash
# Health
curl http://localhost:8000/health

# API Docs (open in browser)
http://localhost:8000/docs

# Example: Create game
curl -X POST http://localhost:8000/api/game/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"difficulty": "medium", "color": "white"}'
```

### Reset Everything

```bash
# Docker Compose: Remove all containers and volumes
docker compose down -v

# Start fresh
docker compose up -d --build
```

### View Game Data (Redis)

```bash
# Docker Compose
docker exec -it chess_redis redis-cli

# Or locally
redis-cli

# Inside redis-cli:
KEYS *                    # See all keys
GET game:abc123:state     # Get specific game
DBSIZE                    # Total keys
FLUSHDB                   # Clear database (⚠️ careful!)
```

---

## Environment Variables

Key variables in `.env`:

| Variable | Example | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | `1234567:ABC...` | From @BotFather |
| `TELEGRAM_BOT_USERNAME` | `my_chess_bot` | Bot username (no @) |
| `APP_ENV` | `development` | development or production |
| `STOCKFISH_PATH` | `/usr/games/stockfish` | Path to Stockfish binary |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |

Full documentation: [backend/.env.example](backend/.env.example)

---

## Troubleshooting

### "Bot doesn't respond"

```bash
# Check bot process
docker compose logs api | grep -i "bot\|running"

# Verify token
grep TELEGRAM_BOT_TOKEN backend/.env

# Check health endpoint
curl http://localhost:8000/health
```

### "Connection refused" (Redis)

```bash
# Ensure Redis is running
docker compose ps redis  # Docker Compose
redis-cli ping           # Local Redis

# Start Redis if needed
docker compose up -d redis
```

### "Stockfish not found"

```bash
# Docker Compose: Already installed
docker exec chess_api which stockfish

# Local: Install via package manager
# Ubuntu: sudo apt-get install stockfish
# macOS: brew install stockfish
# Windows: Download from stockfishchess.org
```

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
# Docker: Edit docker-compose.yml ports
# Local: uvicorn app.main:app --port 8001
```

### Frontend won't load

```bash
# Check frontend is built
docker compose logs frontend

# Check Nginx config
docker compose logs nginx

# Browser console for errors
# Dev tools (F12) → Console tab
```

---

## Development Workflow

### Making Changes

1. **Backend**: Edit `.py` files in `backend/app/`
   - API auto-reloads with `--reload` flag
   - Check logs for errors

2. **Frontend**: Edit `.tsx` files in `frontend/src/`
   - Vite hot-reloads on save
   - Check browser console for errors

3. **Redis Schema**: Changes to game/stats serialization
   - Clear database: `docker exec chess_redis redis-cli FLUSHDB`
   - Restart services: `docker compose restart api`

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
cd backend
flake8 app/

# Type checking
mypy app/

# Frontend linting
cd frontend
npm run lint
```

---

## Next Steps

- **Add a game**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production setup
- **Troubleshoot**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- **API Reference**: See [backend/README.md](backend/README.md) for API documentation

---

## Getting Help

- **Logs**: Always check `docker compose logs api` or console output first
- **Issues**: [GitHub Issues](https://github.com/Mukller/chess/issues)
- **Status Page**: `/health` endpoint shows system status
- **Debug Mode**: Set `APP_LOG_LEVEL=DEBUG` in `.env`

---

## Quick Commands Reference

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View logs
docker compose logs -f api

# Enter container shell
docker exec -it chess_api /bin/bash

# Rebuild after code changes
docker compose up -d --build

# Clear all data
docker compose down -v

# Check health
curl http://localhost:8000/health

# Redis CLI
docker exec -it chess_redis redis-cli
```

Happy coding! 🎉
