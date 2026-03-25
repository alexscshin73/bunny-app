#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT_DIR/run"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
USER_DOMAIN="gui/$(id -u)"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
TUNNEL_PID_FILE="$RUN_DIR/tunnel.pid"
BACKEND_LABEL="com.sclshin.bunny.backend"
TUNNEL_LABEL="com.sclshin.bunny.tunnel"
BACKEND_PLIST="$LAUNCH_AGENTS_DIR/$BACKEND_LABEL.plist"
TUNNEL_PLIST="$LAUNCH_AGENTS_DIR/$TUNNEL_LABEL.plist"
BACKEND_HEALTH_URL="${BUNNY_BACKEND_HEALTH_URL:-http://127.0.0.1:8000/healthz}"
PUBLIC_URL="${BUNNY_PUBLIC_URL:-https://bunny.carroamix.com}"
PUBLIC_HEALTH_URL="${BUNNY_PUBLIC_HEALTH_URL:-$PUBLIC_URL/healthz}"

launch_agent_installed() {
  local plist_path="$1"
  [ -f "$plist_path" ]
}

report_launch_agent() {
  local label="$1"
  local plist_path="$2"
  local name="$3"

  if ! launch_agent_installed "$plist_path"; then
    return 1
  fi

  if launchctl print "$USER_DOMAIN/$label" >/dev/null 2>&1; then
    local pid
    pid="$(launchctl print "$USER_DOMAIN/$label" | awk -F'= ' '/^[[:space:]]*pid = / {print $2; exit}')"
    if [ -n "$pid" ]; then
      echo "$name: launchd running (pid $pid)"
    else
      echo "$name: launchd loaded"
    fi
  else
    echo "$name: launchd installed, not loaded"
  fi

  return 0
}

report_pid_file() {
  local label="$1"
  local path="$2"

  if [ ! -f "$path" ]; then
    echo "$label: not running"
    return
  fi

  local pid
  pid="$(tr -d '\n' < "$path")"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "$label: running (pid $pid)"
  else
    echo "$label: stale pid file"
  fi
}

if ! report_launch_agent "$BACKEND_LABEL" "$BACKEND_PLIST" "Backend"; then
  report_pid_file "Backend" "$BACKEND_PID_FILE"
fi

if ! report_launch_agent "$TUNNEL_LABEL" "$TUNNEL_PLIST" "Tunnel"; then
  report_pid_file "Tunnel" "$TUNNEL_PID_FILE"
fi

if curl -s --max-time 5 "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
  echo "Local health: ok"
else
  echo "Local health: unreachable"
fi

if curl -s --max-time 10 "$PUBLIC_HEALTH_URL" >/dev/null 2>&1; then
  echo "Public health: ok"
else
  echo "Public health: unreachable"
fi

echo "Public URL: $PUBLIC_URL"
