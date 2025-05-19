#!/usr/bin/env bash

# Cross-platform cleanup script for MyChatBot Docker resources

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Function to safely remove resources
safe_remove() {
  local filter="$1"
  local type="$2"
  
  echo "Removing $type with filter: $filter"
  if ! docker "$type" ls --filter "$filter" --format "{{.ID}}" | xargs -r docker "$type" rm -f 2>/dev/null; then
    echo "No $type to remove"
  fi
}

# Stop and remove containers
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose -f "docker-compose.yml" down || true
fi

# Remove project-specific resources
safe_remove "label=project=mychatbot" "container"
safe_remove "label=project=mychatbot" "image"
safe_remove "name=mychatbot" "network"
safe_remove "name=mychatbot" "volume"

# Cleanup builder cache
docker builder prune -f --filter "label=project=mychatbot" 2>/dev/null || true

# Cleanup networks (not associated with containers)
docker network prune -f 2>/dev/null || true

echo "Cleanup complete"