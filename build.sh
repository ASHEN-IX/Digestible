#!/bin/bash
# Build script with optimizations for Digestible

set -e

echo "Building Digestible services with optimizations..."

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with progress and no cache for troubleshooting
docker compose build --progress=plain --no-cache

echo "Build completed successfully!"