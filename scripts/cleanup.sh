#!/bin/bash
# Cleanup script for Phase 0 migration

echo "🧹 Cleaning up old Phase 0 files..."

# Remove old app directory
if [ -d "app" ]; then
    echo "Removing old app/ directory..."
    rm -rf app/
fi

# Remove old alembic backup
if [ -f "alembic/env.py.old" ]; then
    echo "Removing alembic env backup..."
    rm -f alembic/env.py.old
fi

# Remove old migration files if any
if [ -d "alembic/versions" ]; then
    echo "Backing up old migrations..."
    mkdir -p .old_migrations
    mv alembic/versions/* .old_migrations/ 2>/dev/null || true
fi

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove old environment files if they exist
if [ -f ".env.production" ] && [ ! -f ".env" ]; then
    echo "Renaming .env.production to .env..."
    mv .env.production .env
fi

echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Review your .env file"
echo "2. Run: docker compose up -d"
echo "3. Run: docker compose exec backend alembic revision --autogenerate -m 'phase 0 schema'"
echo "4. Run: docker compose exec backend alembic upgrade head"
