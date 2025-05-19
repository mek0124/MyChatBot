#!/bin/bash

function runCommand() {
  echo -e "Running: $*"
  "$@"
  local status=$?

  if [ $status -ne 0 ]; then
    echo -e "Error: Command: '$*' failed with exit code $status" >&2
    exit $status
  fi

  return 0
}

clear

echo -e "Starting Build Process... Please Wait..."
sleep 2

# Run commands sequentially
runCommand python3 linux_build.py
runCommand python3 mac_build.py
runCommand python3 windows_build.py
runCommand bash ./cleanup.sh
runCommand bash ./build.sh
runCommand bash ./run.sh

echo -e "All commands completed successfully!"