#!/bin/bash
# Script to switch between development and production environments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

ENV_TYPE=$1

if [ -z "$ENV_TYPE" ]; then
    echo "Usage: ./scripts/switch-env.sh [dev|production]"
    echo ""
    echo "Current environment:"
    if [ -f "$ROOT_DIR/.env" ]; then
        if grep -q "development" "$ROOT_DIR/.env" 2>/dev/null; then
            echo "  → Development (local services)"
        elif grep -q "production" "$ROOT_DIR/.env" 2>/dev/null; then
            echo "  → Production (Neon database)"
        else
            echo "  → Unknown (check .env file)"
        fi
    else
        echo "  → No .env file found"
    fi
    echo ""
    echo "Available environments:"
    echo "  dev        - Use local Docker services (PostgreSQL + Redis)"
    echo "  production - Use Neon PostgreSQL and production services"
    exit 1
fi

case $ENV_TYPE in
    dev|development)
        echo "Switching to DEVELOPMENT environment..."
        cp "$ROOT_DIR/.env.dev" "$ROOT_DIR/.env"
        echo "✓ Switched to development environment"
        echo ""
        echo "Configuration:"
        echo "  Database: Local PostgreSQL (Docker Compose)"
        echo "  Redis:    Local Redis (Docker Compose)"
        echo "  Debug:    Enabled"
        echo ""
        echo "Start services with: docker-compose up"
        ;;
    
    prod|production)
        echo "Switching to PRODUCTION environment..."
        cp "$ROOT_DIR/.env.production" "$ROOT_DIR/.env"
        echo "✓ Switched to production environment"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your Neon credentials!"
        echo ""
        echo "Configuration:"
        echo "  Database: Neon PostgreSQL (serverless)"
        echo "  Redis:    Production Redis"
        echo "  Debug:    Disabled"
        echo ""
        echo "Next steps:"
        echo "  1. Edit .env with your Neon database credentials"
        echo "  2. Run: docker-compose up"
        echo "  3. Run migrations: docker-compose run backend alembic upgrade head"
        ;;
    
    *)
        echo "Error: Unknown environment '$ENV_TYPE'"
        echo "Use 'dev' or 'production'"
        exit 1
        ;;
esac

echo ""
echo "Restart your services for changes to take effect."
