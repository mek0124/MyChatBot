#!/usr/bin/env bash

# Cross-platform build script for MyChatBot Docker image

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Build using compose (preferred)
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose build --no-cache
elif command -v docker &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker build -t mychatbot:latest \
    --label "project=mychatbot" \
    --label "maintainer=$(whoami)@$(hostname)" \
    .
else
  echo "Error: Neither docker-compose nor docker command found"
  exit 1
fi

echo "Build completed successfully"