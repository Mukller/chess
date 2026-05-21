# Deployment Guide

This guide covers deploying the Telegram Chess Bot to production.

## Prerequisites

- Linux server (Ubuntu 22.04 LTS or newer recommended)
- Docker & Docker Compose
- Domain name with DNS configured
- Telegram Bot Token (from @BotFather)

## Step 1: Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Clone repository
git clone https://github.com/Mukller/chess.git
cd chess
```

## Step 2: Configure Environment

```bash
# Copy and edit environment template
cp backend/.env.example backend/.env
nano backend/.env

# Required changes for production:
# - TELEGRAM_BOT_TOKEN: Your bot token from @BotFather
# - TELEGRAM_BOT_USERNAME: Your bot username (without @)
# - TELEGRAM_WEBAPP_URL: https://your-domain.com/app
# - APP_ENV: production
# - APP_SECRET_KEY: Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(48))"
# - CORS_ORIGINS: ["https://your-domain.com"]
# - STOCKFISH_PATH: /usr/games/stockfish (default)
# - REDIS_URL: redis://redis:6379/0 (when using Docker Compose)
```

## Step 3: SSL/TLS Setup (with Caddy)

Create `docker-compose.override.yml` for production:

```yaml
version: "3.9"

services:
  caddy:
    image: caddy:latest
    container_name: chess_caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    environment:
      - ACME_AGREE=true
    networks:
      - chess_net
    depends_on:
      - nginx

  # Remove nginx port binding - Caddy handles 80/443
  nginx:
    ports: []
    expose:
      - "80"

volumes:
  caddy_data:
  caddy_config:

networks:
  chess_net:
    driver: bridge
```

Create `Caddyfile`:

```caddy
your-domain.com {
    reverse_proxy nginx:80
    
    # Enable HTTPS automatically via Let's Encrypt
    encode gzip
    
    # HSTS header
    header / {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options nosniff
        X-Frame-Options "ALLOW-FROM https://web.telegram.org"
    }
}
```

## Step 4: Deploy

```bash
# Build and start services
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

# Verify services are running
docker compose ps

# Check logs
docker compose logs -f api
docker compose logs -f redis
```

## Step 5: Configure Telegram Bot

1. Open [@BotFather](https://t.me/BotFather)
2. Select your bot with `/mybots`
3. Choose **Bot Settings** → **Menu Button**
4. Set as: Web App
5. URL: `https://your-domain.com/app`
6. Text: "Play Chess"

Optional: Set bot description, short description, and commands.

## Step 6: Verify Deployment

```bash
# Check health endpoint
curl https://your-domain.com/health

# Monitor logs
docker compose logs -f --tail=50

# Test bot in Telegram
# Open bot, tap Menu Button (or /start) → should see game options
```

## Production Checklist

- [ ] HTTPS enabled with valid certificate
- [ ] `APP_ENV=production`
- [ ] `APP_SECRET_KEY` is a long random string
- [ ] `CORS_ORIGINS` restricted to your domain
- [ ] `TELEGRAM_WEBAPP_URL` set to HTTPS URL
- [ ] Redis persistence enabled (check `docker-compose.yml` appendonly setting)
- [ ] Database backups scheduled (Redis volume backup)
- [ ] Monitoring/alerting configured
- [ ] Rate limiting tested
- [ ] Stockfish path verified in container (`docker exec chess_api which stockfish`)

## Monitoring & Logs

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f redis

# Last N lines
docker compose logs --tail=100 api
```

### Health Check Endpoint

```bash
# Returns service status
curl https://your-domain.com/health

# Response:
# {
#   "status": "ok",
#   "version": "1.2.0",
#   "engine_ready": true,
#   "bot_configured": true
# }
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker exec -it chess_redis redis-cli

# Check memory usage
info memory

# List keys
keys *

# Monitor commands in real-time
monitor
```

## Backup & Recovery

### Backup Redis Data

```bash
# Manual backup
docker exec chess_redis redis-cli BGSAVE

# Copy Redis volume
docker run --rm -v chess_redis_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz /data
```

### Restore from Backup

```bash
# Extract backup
tar xzf redis-backup.tar.gz -C /

# Restart Redis
docker compose restart redis
```

## Troubleshooting

### Bot doesn't respond

```bash
# Check bot is running
docker compose ps api

# Check logs for errors
docker compose logs api | tail -50

# Verify token
echo "Check TELEGRAM_BOT_TOKEN in .env"

# Test health endpoint
curl https://your-domain.com/health
```

### WebApp doesn't load

```bash
# Check frontend is built
docker compose logs frontend

# Verify Nginx config
docker compose logs nginx

# Check CORS headers
curl -I https://your-domain.com/api/game/list
```

### Stockfish not found

```bash
# Check inside container
docker exec chess_api which stockfish

# If missing, rebuild with stockfish package
# Edit Dockerfile to ensure stockfish is installed
docker compose build --no-cache api
```

### High memory usage

```bash
# Check Redis memory
docker exec chess_redis redis-cli info memory

# Check game TTL
# Games should expire after REDIS_GAME_TTL_SECONDS (default 86400 = 1 day)
# History has 5-year TTL

# Clear old keys if needed
docker exec chess_redis redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'game:*')))" 0
```

## Scaling Considerations

### Horizontal Scaling

To run multiple API instances, use a load balancer:

```yaml
# Add to docker-compose.override.yml
services:
  api_1:
    # Copy api service config
    container_name: chess_api_1
  api_2:
    # Copy api service config  
    container_name: chess_api_2
  
  # Update Nginx upstream
```

Update `nginx/nginx.conf`:

```nginx
upstream chess_api {
    server api_1:8000;
    server api_2:8000;
}
```

### Redis Persistence

Current setup uses:
- `appendonly yes` — writes every command to disk
- `maxmemory-policy allkeys-lru` — evicts oldest keys when full
- `maxmemory 256mb` — adjust based on your server

## Performance Tuning

### Stockfish Workers

Adjust `STOCKFISH_WORKERS` based on CPU cores:

```bash
# Get CPU count
nproc

# Set in .env: STOCKFISH_WORKERS = (nproc / 2)
# Example: 8-core server → STOCKFISH_WORKERS=4
```

### Uvicorn Workers

For multiple API instances, uvicorn runs single-threaded. Docker Compose manages multiple containers.

## Support & Issues

- Report bugs: [GitHub Issues](https://github.com/Mukller/chess/issues)
- Check logs first for error details
- Verify configuration matches production checklist

## Security Notes

- Keep Docker and base images updated
- Use strong `APP_SECRET_KEY` (minimum 32 random characters)
- Restrict CORS to your domain only
- Use HTTPS everywhere (no HTTP in production)
- Regularly backup Redis volume
- Monitor rate limiting for abuse patterns
