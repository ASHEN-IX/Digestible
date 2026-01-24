# Digestible - Browser Extension Only

A streamlined article processing platform that works entirely through your browser extension. No accounts, no dashboards - just save articles and get notifications when they're ready.

## 🚀 Quick Start

### 1. Start the Application
```bash
cd /path/to/digestible
./manage.sh start
```

### 2. Install the Browser Extension
- Open Chrome → `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked"
- Select the `browser-extension/` folder

### 3. Use It
- Click the extension icon on any webpage
- Click "Save Article"
- Get notified when processing is complete
- View your saved articles in the extension

## 📋 Features

### ✅ What It Does
- **One-click article saving** from any webpage
- **Automatic processing** in the background
- **Browser notifications** when articles are ready
- **Local storage** - articles saved in your browser
- **No accounts required** - works immediately

### ✅ Technical Features
- **FastAPI backend** for article processing
- **PostgreSQL database** for data storage
- **Redis queue** for background processing
- **Docker containers** for easy deployment
- **Chrome extension** with modern UI

## 🛠️ Management

```bash
# Start all services
./manage.sh start

# Stop all services
./manage.sh stop

# Check status
./manage.sh status

# View logs
./manage.sh logs backend
./manage.sh logs

# Restart services
./manage.sh restart
```

## 🔧 Architecture

```
┌─────────────────┐
│  Browser        │
│  Extension      │ ← Stores articles locally
│  (Chrome)       │ ← Shows notifications
└─────────────────┘
        │
        ▼
┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │────│   PostgreSQL    │
│   Backend       │    │   Database      │
│   (Processing)  │    └─────────────────┘
└─────────────────┘           ▲
        │                     │
        ▼                     │
┌─────────────────┐           │
│   Redis Queue   │ ──────────┘
│   (Background   │
│    Tasks)       │
└─────────────────┘
```

## 📱 Browser Extension

### Features
- **Popup Interface**: Clean, modern design
- **Article List**: View all your saved articles
- **Status Tracking**: See processing progress
- **Local Storage**: Articles stored in browser
### Files
- `manifest.json` - Extension configuration
- `popup.html/js` - Main interface
- `background.js` - Background processing & notifications
- `styles.css` - Modern UI styling

## 🔌 API Endpoints

- `POST /api/v1/articles` - Submit article for processing
- `GET /api/v1/articles` - List all articles
- `GET /api/v1/articles/{id}` - Get specific article
- `GET /health` - Health check

## 💾 Data Storage

- **Server**: PostgreSQL database stores processed articles
- **Browser**: Chrome local storage keeps article list and metadata
- **Automatic Sync**: Extension polls server for updates

## 🚨 Troubleshooting

### Extension Not Working
1. Check extension is loaded: `chrome://extensions/`
2. Check API is running: `curl http://localhost:8000/health`
3. Check browser console for errors

### Services Not Starting
```bash
# Check Docker
docker info

# Check logs
./manage.sh logs

# Restart
./manage.sh restart
```

### Database Issues
```bash
# Reset database
./manage.sh stop
docker volume rm digestible_postgres_data
./manage.sh start
```

### Services Won't Start (Advanced)
```bash
# Check logs
docker compose logs

# Rebuild containers
docker compose down
docker compose up --build
```

### Database Connection Issues
```bash
# Test connection
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

## 🔄 Development

### Backend Development
- Code changes auto-reload
- Check logs: `./manage.sh logs backend`
- API docs: `http://localhost:8000/docs`

### Extension Development
- Edit files in `browser-extension/`
- Reload extension in `chrome://extensions/`
- Test with live API

## 📊 Performance

- **Processing Time**: 10-30 seconds per article
- **Storage**: Unlimited articles (server-side)
- **Offline**: Access saved articles without internet
- **Sync**: Automatic updates when online

## 🎯 Use Cases

- **Research**: Save articles for later reading
- **Content Creation**: Collect sources and references
- **Learning**: Build personal knowledge base
- **Productivity**: Quick article processing and summaries



**Ready to save your first article?** 🚀

```bash
./manage.sh start
# Then load the extension and start saving!
```

## 🔄 Development

### Backend Development
- Code changes auto-reload
- Check logs: `./manage.sh logs backend`
- API docs: `http://localhost:8000/docs`

### Extension Development
- Edit files in `browser-extension/`
- Reload extension in `chrome://extensions/`
- Test with live API

### Code Quality
```bash
# Python linting (backend)
docker compose exec backend black backend/
docker compose exec backend ruff check backend/
```

### Testing
```bash
# FastAPI tests
docker compose exec backend pytest

# Browser extension tests
./test-ci-local.sh
```

### Database Changes
```bash
# FastAPI schema changes
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```

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
Store in PostgreSQL
    ↓
Browser extension displays results
```

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string

### Optional
- `REDIS_URL` - Redis connection (defaults to `redis://redis:6379/0`)
- `DEBUG` - Enable debug mode (default: true)

## Deployment

### Docker Images

The project provides pre-built Docker images available on both GitHub Container Registry and DockerHub:

#### DockerHub
- **Repository**: [vanistas/digestible-backend](https://hub.docker.com/repository/docker/vanistas/digestible-backend/)
- **Latest Image**: `docker pull vanistas/digestible-backend:latest`
- **Tags**: `latest`, branch-specific tags, and commit SHAs

#### GitHub Container Registry
- **Repository**: `ghcr.io/ASHEN-IX/digestible/backend`
- **Latest Image**: `docker pull ghcr.io/ASHEN-IX/digestible/backend:latest`

#### Usage Examples

**Run with Docker Compose (Recommended):**
```bash
docker compose up -d
```

**Run Backend Only:**
```bash
# Using DockerHub image
docker run -d \
  --name digestible-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  vanistas/digestible-backend:latest

# Using GHCR image
docker run -d \
  --name digestible-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  ghcr.io/ASHEN-IX/digestible/backend:latest
```

**Manual Deployment:**
```bash
# Build images locally
docker build -f Dockerfile.api -t digestible-backend .

# Or use published images
docker build -f Dockerfile.api -t digestible-backend .
docker build -f dashboard/Dockerfile -t digestible-dashboard .

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline

The CI/CD pipeline automatically:
- Runs tests on every push to `main` and `develop` branches
- Builds Docker images on successful tests
- Pushes images to both GitHub Container Registry and DockerHub
- Deploys to production environment (when configured)

**Workflow Status**: [GitHub Actions](https://github.com/ASHEN-IX/Digestible/actions)


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `docker compose exec backend pytest`
5. Submit a pull request


---

