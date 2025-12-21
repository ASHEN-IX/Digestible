#!/bin/bash

# Digestible Application Manager
# This script helps you start, stop, and manage the Digestible application

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to start the application
start_app() {
    print_info "Starting Digestible application..."

    # Stop any existing containers
    docker compose down >/dev/null 2>&1 || true

    # Start all services
    docker compose up -d

    # Wait for services to be healthy
    print_info "Waiting for services to start..."
    sleep 10

    # Check if services are running
    if docker compose ps | grep -q "Up"; then
        print_status "✅ Digestible application started successfully!"
        print_info "🌐 Backend API: http://localhost:8000"
        print_info "📊 Health check: http://localhost:8000/health"
    else
        print_error "❌ Some services failed to start. Check logs with: docker compose logs"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_info "Stopping Digestible application..."
    docker compose down
    print_status "✅ Digestible application stopped."
}

# Function to restart the application
restart_app() {
    print_info "Restarting Digestible application..."
    stop_app
    sleep 2
    start_app
}

# Function to show status
show_status() {
    print_info "Digestible Application Status:"
    echo ""
    docker compose ps
    echo ""
    print_info "Service URLs:"
    print_info "🌐 Backend API: http://localhost:8000"
    print_info "📊 Health check: http://localhost:8000/health"
    print_info "🔌 Browser Extension: Load from browser-extension/ folder"
}

# Function to show logs
show_logs() {
    if [ -n "$2" ]; then
        docker compose logs -f "$2"
    else
        docker compose logs -f
    fi
}

# Function to run database migrations
run_migrations() {
    print_info "Running database migrations..."
    docker compose exec backend alembic upgrade head
    print_status "✅ Database migrations completed."
}

# Function to rebuild containers
rebuild_app() {
    print_info "Rebuilding application containers..."
    docker compose down
    docker compose build --no-cache
    start_app
}

# Function to clean up
cleanup_app() {
    print_info "Cleaning up Docker resources..."
    docker compose down -v
    docker system prune -f
    print_status "✅ Cleanup completed."
}

# Main script logic
case "${1:-help}" in
    start)
        check_docker
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        check_docker
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    migrate)
        check_docker
        run_migrations
        ;;
    rebuild)
        check_docker
        rebuild_app
        ;;
    cleanup)
        cleanup_app
        ;;
    help|*)
        echo "Digestible Application Manager"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  start     Start the application"
        echo "  stop      Stop the application"
        echo "  restart   Restart the application"
        echo "  status    Show application status"
        echo "  logs      Show application logs (add service name for specific logs)"
        echo "  migrate   Run database migrations"
        echo "  rebuild   Rebuild all containers"
        echo "  cleanup   Clean up Docker resources"
        echo "  help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start the application"
        echo "  $0 logs backend   # Show backend logs"
        echo "  $0 migrate        # Run database migrations"
        ;;
esac