# Environment Configuration Guide

This project uses environment-specific configuration files to easily switch between development and production environments.

## Environment Files

- **`.env.dev`** - Development environment (local Docker services)
- **`.env.production`** - Production environment (Neon PostgreSQL)
- **`.env`** - Active environment (auto-generated, DO NOT commit)
- **`.env.example`** - Template for reference

## Quick Start

### Switch to Development Environment

```bash
./scripts/switch-env.sh dev
```

This configures the system to use:
- Local PostgreSQL (via Docker Compose)
- Local Redis (via Docker Compose)
- Debug mode enabled

### Switch to Production Environment

```bash
./scripts/switch-env.sh production
```

**Important:** After switching to production, edit `.env` and add your Neon database credentials.

This configures the system to use:
- Neon PostgreSQL (serverless)
- Production Redis
- Debug mode disabled

## Setting Up Neon Database

1. Switch to production environment:
   ```bash
   ./scripts/switch-env.sh production
   ```

2. Get your Neon database connection string from: https://neon.tech/

3. Edit `.env` and replace the DATABASE_URL:
   ```
   DATABASE_URL=postgresql+asyncpg://[username]:[password]@[host]/[database]?sslmode=require
   ```

4. Start the services:
   ```bash
   docker-compose up
   ```

5. Run migrations to create the database schema:
   ```bash
   docker-compose run backend alembic upgrade head
   ```

## Environment Variables Explained

### Database Configuration

- **`DATABASE_URL`** - SQLAlchemy connection string for FastAPI (async)
- **`DATABASE_NAME`** - Database name for Django
- **`DATABASE_USER`** - Database username for Django
- **`DATABASE_PASSWORD`** - Database password for Django
- **`DATABASE_HOST`** - Database host
- **`DATABASE_PORT`** - Database port (default: 5432)

### Redis Configuration

- **`REDIS_URL`** - Redis connection string for caching/queuing

### Application Settings

- **`ENVIRONMENT`** - Current environment (development/production)
- **`DEBUG`** - Enable/disable debug mode
- **`DJANGO_SECRET_KEY`** - Django secret key (generate unique for production)
- **`ALLOWED_HOSTS`** - Comma-separated list of allowed hosts

### Pipeline Settings

- **`MAX_CONTENT_LENGTH`** - Maximum article size in bytes
- **`CHUNK_SIZE`** - Characters per chunk for processing
- **`MAX_CHUNKS`** - Maximum number of chunks per article

## Testing Different Environments

### Test Development Environment

```bash
# Switch to dev
./scripts/switch-env.sh dev

# Start services
docker-compose up -d

# Run tests
docker-compose run backend pytest tests/backend/ -v
```

### Test Production Environment (with Neon)

```bash
# Switch to production
./scripts/switch-env.sh production

# Edit .env with your Neon credentials

# Start services
docker-compose up -d

# Run migrations
docker-compose run backend alembic upgrade head

# Test the API
curl http://localhost:8000/health
```

## Security Notes

- ⚠️ **NEVER commit `.env` files** - They are in `.gitignore`
- ✓ `.env.dev` and `.env.production` are templates and can be committed
- 🔒 Generate a strong `DJANGO_SECRET_KEY` for production
- 🔐 Use strong passwords for production databases
- 🚫 Set `DEBUG=false` in production

## Troubleshooting

### Issue: "Permission denied" when running switch-env.sh

```bash
chmod +x scripts/switch-env.sh
```

### Issue: Database connection refused

Make sure Docker services are running:
```bash
docker-compose up -d postgres redis
```

### Issue: Neon connection times out

1. Check your DATABASE_URL is correct
2. Ensure `sslmode=require` is in the connection string
3. Verify your Neon project is active (not suspended)

### Check Current Environment

```bash
./scripts/switch-env.sh
```

This shows which environment is currently active.
