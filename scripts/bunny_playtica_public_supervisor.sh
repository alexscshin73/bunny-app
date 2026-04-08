#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INTERVAL_SECONDS="${BUNNY_PLAYTICA_SUPERVISOR_INTERVAL_SECONDS:-60}"
INITIAL_DELAY_SECONDS="${BUNNY_PLAYTICA_SUPERVISOR_INITIAL_DELAY_SECONDS:-10}"

shutdown() {
  echo "Stopping Bunny Playtica public supervisor..."
  bash "$ROOT_DIR/scripts/bunny_playtica_public_stop.sh" >/dev/null 2>&1 || true
  exit 0
}

trap shutdown INT TERM HUP

echo "Starting Bunny Playtica public supervisor."
echo "Initial delay: ${INITIAL_DELAY_SECONDS}s"
echo "Health check interval: ${INTERVAL_SECONDS}s"

sleep "$INITIAL_DELAY_SECONDS"

while true; do
  if ! bash "$ROOT_DIR/scripts/bunny_playtica_public_start.sh"; then
    echo "Bunny Playtica start attempt failed; retrying in ${INTERVAL_SECONDS}s"
  fi
  sleep "$INTERVAL_SECONDS" &
  wait "$!"
done
