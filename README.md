# Digestible - Phase 0 Complete! 🎉

[![CI/CD Pipeline](https://github.com/kammounmedaziz/Digestible/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/kammounmedaziz/Digestible/actions/workflows/ci-cd.yml)
[![Docker Build](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)

Turn your 'Read Later' graveyard into an active audio playlist.

## ✅ Phase 0: Foundation & DevOps Complete

**All Phase 0 requirements implemented:**
- ✅ **Dockerized Django + FastAPI + Redis + Postgres** - Full containerized stack
- ✅ **.env for secrets + config** - Comprehensive environment management
- ✅ **Prettier + lint for Python + JS** - Code quality tools configured
- ✅ **CI/CD pipeline** - GitHub Actions for build, test, and deployment

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django        │    │   FastAPI       │    │   Redis         │
│   Dashboard     │◄──►│   Backend       │◄──►│   Queue/Cache   │
│   (Port 8001)   │    │   (Port 8000)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Neon Postgres │
                    │   (Cloud DB)    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for dashboard development)

### Local Development
```bash
# Clone the repository
git clone https://github.com/kammounmedaziz/Digestible.git
cd Digestible

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Run tests
./build.sh test
```

### Services
- **Backend API**: http://localhost:8000 (FastAPI)
- **Dashboard**: http://localhost:8001 (Django)
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

```
digestible/
├── backend/              # FastAPI ingestion worker
│   ├── api/             # API endpoints
│   ├── pipeline/        # Processing pipeline stages
│   ├── database/        # DB models & connections
│   └── config/          # Configuration
├── dashboard/           # Django dashboard & user auth
│   ├── users/          # User management
│   ├── articles/       # Article management
│   ├── dashboard/      # Main dashboard app
│   └── digestible/     # Django project settings
├── shared/              # Shared utilities
├── .github/workflows/   # CI/CD pipelines
└── docker-compose.yml   # Multi-service orchestration
```

## Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
# Edit .env with your Neon DATABASE_URL and generate DJANGO_SECRET_KEY
```

### 2. Start All Services
```bash
docker compose up -d
```

### 3. Run Database Migrations
```bash
# FastAPI backend migrations
docker compose exec backend alembic upgrade head

# Django dashboard migrations
docker compose exec dashboard python manage.py migrate
```

### 4. Create Admin User
```bash
docker compose exec dashboard python manage.py createsuperuser
```

### 5. Access Applications
- **Django Dashboard**: http://localhost:8001
- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Django Admin**: http://localhost:8001/admin

## Development Workflow

### Code Quality
```bash
# Python linting (backend)
docker compose exec backend black backend/
docker compose exec backend ruff check backend/

# JavaScript linting (dashboard)
cd dashboard && npm run lint && npm run format
```

### Testing
```bash
# FastAPI tests
docker compose exec backend pytest

# Django tests
docker compose exec dashboard python manage.py test
```

### Database Changes
```bash
# FastAPI schema changes
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head

# Django model changes
docker compose exec dashboard python manage.py makemigrations
docker compose exec dashboard python manage.py migrate
```

## API Endpoints

### FastAPI Backend (Port 8000)
- `POST /api/v1/articles` - Submit article for processing
- `GET /api/v1/articles/{id}` - Get article status/details
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation

### Django API (Port 8001)
- `GET /api/users/me/` - Current user info
- `GET /api/articles/` - User's articles
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

## Pipeline Flow

Articles submitted to FastAPI go through this async pipeline:

```
User submits URL
    ↓
FastAPI receives → Creates DB record
    ↓
Background task starts
    ↓
┌──────────────────────────────────┐
│  1. FETCH    → Download HTML      │
│  2. PARSE    → Extract text       │
│  3. CHUNK    → Split into parts   │
│  4. SUMMARIZE → Generate summary  │ ← Phase 1: AI integration
│  5. RENDER   → Output formats     │ ← Phase 1: TTS/audio
└──────────────────────────────────┘
    ↓
Store in Neon Postgres
    ↓
Django dashboard displays results
```

## Environment Variables

### Required
- `DATABASE_URL` - Neon Postgres connection string
- `DJANGO_SECRET_KEY` - Django secret key (generate randomly)

### Optional
- `REDIS_URL` - Redis connection (defaults to `redis://redis:6379/0`)
- `DEBUG` - Enable debug mode (default: true)
- `FASTAPI_URL` - FastAPI backend URL for Django (default: http://localhost:8000)

## Deployment

### Local Development
```bash
docker compose up -d
```

### Production
The CI/CD pipeline automatically:
- Runs tests on every push
- Builds Docker images on main branch
- Pushes to GitHub Container Registry
- Deploys to production environment

### Manual Deployment
```bash
# Build images
docker build -f Dockerfile.api -t digestible-backend .
docker build -f dashboard/Dockerfile -t digestible-dashboard .

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

## Phase 1 Preview

**Coming next:**
- 🤖 **AI Summarization** - Replace placeholder with OpenAI/Claude
- 🔊 **TTS Audio Rendering** - Text-to-speech integration
- 🌐 **Chrome Extension** - One-click article saving
- 📊 **Advanced Analytics** - Usage statistics and insights
- 🎨 **Enhanced UI** - Modern dashboard with React/Vue

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs

# Rebuild containers
docker compose down
docker compose up --build
```

### Database Connection Issues
```bash
# Test Neon connection
docker compose exec backend python -c "from backend.database import engine; import asyncio; asyncio.run(engine.connect())"

# Reset migrations
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `docker compose exec backend pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Phase 0 Complete!** 🚀 Ready for Phase 1 development.

### Linting & Formatting
```bash
ruff check backend/
black backend/
```

### Database Migrations
```bash
# Create migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head
```

## Architecture

**Phase 0 Pipeline:**
1. **FETCH**: Download HTML content
2. **PARSE**: Extract article text
3. **CHUNK**: Split into processable segments
4. **SUMMARIZE**: Generate summary (placeholder)
5. **RENDER**: Convert to output formats (placeholder)

## Next Steps (Phase 1+)
- Django dashboard for user management
- AI summarization integration
- TTS audio rendering
- Chrome extension
- Production deployment

