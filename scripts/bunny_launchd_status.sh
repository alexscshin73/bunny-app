#!/usr/bin/env bash

set -euo pipefail

USER_DOMAIN="gui/$(id -u)"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_LABEL="com.sclshin.bunny.backend"
TUNNEL_LABEL="com.sclshin.bunny.tunnel"
PUBLIC_URL="${BUNNY_PUBLIC_URL:-https://bunny.carroamix.com}"
PUBLIC_HEALTH_URL="${BUNNY_PUBLIC_HEALTH_URL:-$PUBLIC_URL/healthz}"

report_agent() {
  local label="$1"

  if launchctl print "$USER_DOMAIN/$label" >/dev/null 2>&1; then
    local pid
    pid="$(launchctl print "$USER_DOMAIN/$label" | awk -F'= ' '/^[[:space:]]*pid = / {print $2; exit}')"
    if [ -n "$pid" ]; then
      echo "$label: loaded (pid $pid)"
    else
      echo "$label: loaded"
    fi
  else
    echo "$label: not loaded"
  fi
}

report_agent "$BACKEND_LABEL"
report_agent "$TUNNEL_LABEL"

if curl -s --max-time 5 http://127.0.0.1:8000/healthz >/dev/null 2>&1; then
  echo "Local health: ok"
else
  echo "Local health: unreachable"
fi

if curl -s --max-time 10 "$PUBLIC_HEALTH_URL" >/dev/null 2>&1; then
  echo "Public health: ok"
else
  echo "Public health: unreachable"
fi

echo "Backend log: $ROOT_DIR/run/launchd-backend.log"
echo "Tunnel log: $ROOT_DIR/run/launchd-tunnel.log"
