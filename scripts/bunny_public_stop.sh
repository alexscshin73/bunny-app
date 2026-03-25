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

stop_launch_agent() {
  local label="$1"
  local plist_path="$2"

  if [ ! -f "$plist_path" ]; then
    return 1
  fi

  if launchctl print "$USER_DOMAIN/$label" >/dev/null 2>&1; then
    launchctl bootout "$USER_DOMAIN" "$plist_path" >/dev/null 2>&1 || true
    echo "Stopped $label launch agent."
  else
    echo "$label launch agent is not loaded."
  fi

  return 0
}

stop_from_pid_file() {
  local label="$1"
  local path="$2"

  if [ ! -f "$path" ]; then
    echo "$label is not running."
    return
  fi

  local pid
  pid="$(tr -d '\n' < "$path")"
  if [ -z "$pid" ]; then
    rm -f "$path"
    echo "$label pid file was empty and has been cleared."
    return
  fi

  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "Stopped $label (pid $pid)."
  else
    echo "$label was not running, removed stale pid file."
  fi

  rm -f "$path"
}

if ! stop_launch_agent "$TUNNEL_LABEL" "$TUNNEL_PLIST"; then
  stop_from_pid_file "Cloudflare tunnel" "$TUNNEL_PID_FILE"
fi

if ! stop_launch_agent "$BACKEND_LABEL" "$BACKEND_PLIST"; then
  stop_from_pid_file "bunny-app backend" "$BACKEND_PID_FILE"
fi
