#!/usr/bin/env bash

# Cross-platform run script for MyChatBot

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Detect OS and handle X11 forwarding
case "$(uname -s)" in
  Linux*)
    xhost +local:root >/dev/null 2>&1 || true
    X11_ARGS=(-e "DISPLAY=$DISPLAY" -v "/tmp/.X11-unix:/tmp/.X11-unix")
    ;;
  Darwin*)
    xhost +localhost >/dev/null 2>&1 || true
    X11_ARGS=(-e "DISPLAY=host.docker.internal:0" -v "/tmp/.X11-unix:/tmp/.X11-unix")
    ;;
  *)
    X11_ARGS=()
    ;;
esac

# Run using compose (preferred)
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose -f "docker-compose.yml" up
elif command -v docker &> /dev/null; then
  docker run -it --rm \
    "${X11_ARGS[@]}" \
    -v "$PROJECT_ROOT/.env:/app/.env" \
    -v "$PROJECT_ROOT/backend:/app/backend" \
    --name mychatbot \
    mychatbot:latest
else
  echo "Error: Neither docker-compose nor docker command found"
  exit 1
fi

# Cleanup X11 access
case "$(uname -s)" in
  Linux*) xhost -local:root >/dev/null 2>&1 || true ;;
  Darwin*) xhost -localhost >/dev/null 2>&1 || true ;;
esac