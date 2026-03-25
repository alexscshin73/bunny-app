#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT_DIR/run"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
USER_DOMAIN="gui/$(id -u)"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
TUNNEL_PID_FILE="$RUN_DIR/tunnel.pid"
BACKEND_LOG="$RUN_DIR/backend.log"
TUNNEL_LOG="$RUN_DIR/tunnel.log"
BACKEND_LABEL="com.sclshin.bunny.backend"
TUNNEL_LABEL="com.sclshin.bunny.tunnel"
BACKEND_PLIST="$LAUNCH_AGENTS_DIR/$BACKEND_LABEL.plist"
TUNNEL_PLIST="$LAUNCH_AGENTS_DIR/$TUNNEL_LABEL.plist"
PUBLIC_URL="${BUNNY_PUBLIC_URL:-https://bunny.carroamix.com}"
BACKEND_HEALTH_URL="${BUNNY_BACKEND_HEALTH_URL:-http://127.0.0.1:8000/healthz}"
PUBLIC_HEALTH_URL="${BUNNY_PUBLIC_HEALTH_URL:-$PUBLIC_URL/healthz}"

mkdir -p "$RUN_DIR"

is_pid_running() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

read_pid_file() {
  local path="$1"
  if [ -f "$path" ]; then
    tr -d '\n' < "$path"
  fi
}

cleanup_stale_pid_file() {
  local path="$1"
  local pid
  pid="$(read_pid_file "$path")"
  if [ -n "$pid" ] && ! is_pid_running "$pid"; then
    rm -f "$path"
  fi
}

is_launch_agent_installed() {
  local plist_path="$1"
  [ -f "$plist_path" ]
}

is_launch_agent_loaded() {
  local label="$1"
  launchctl print "$USER_DOMAIN/$label" >/dev/null 2>&1
}

ensure_launch_agent_loaded() {
  local label="$1"
  local plist_path="$2"

  if ! is_launch_agent_installed "$plist_path"; then
    return 1
  fi

  if ! is_launch_agent_loaded "$label"; then
    launchctl bootstrap "$USER_DOMAIN" "$plist_path" >/dev/null 2>&1 || true
  fi

  is_launch_agent_loaded "$label"
}

wait_for_url() {
  local url="$1"
  local attempts="$2"

  for _ in $(seq 1 "$attempts"); do
    if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done

  return 1
}

start_backend() {
  cleanup_stale_pid_file "$BACKEND_PID_FILE"

  if curl -s --max-time 5 "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
    echo "Backend already reachable on $BACKEND_HEALTH_URL"
    return
  fi

  if ensure_launch_agent_loaded "$BACKEND_LABEL" "$BACKEND_PLIST"; then
    echo "Starting bunny-app backend with launchd..."
    launchctl kickstart -k "$USER_DOMAIN/$BACKEND_LABEL"

    if wait_for_url "$BACKEND_HEALTH_URL" 30; then
      echo "Backend is ready."
      return
    fi

    echo "Backend did not become ready in time."
    echo "Recent backend log:"
    tail -n 40 "$ROOT_DIR/run/launchd-backend.log" || true
    exit 1
  fi

  echo "Starting bunny-app backend..."
  nohup bash "$ROOT_DIR/scripts/run_real_demo.sh" >"$BACKEND_LOG" 2>&1 &
  echo "$!" >"$BACKEND_PID_FILE"

  if wait_for_url "$BACKEND_HEALTH_URL" 30; then
    echo "Backend is ready."
    return
  fi

  echo "Backend did not become ready in time."
  echo "Recent backend log:"
  tail -n 40 "$BACKEND_LOG" || true
  exit 1
}

start_tunnel() {
  cleanup_stale_pid_file "$TUNNEL_PID_FILE"

  if ensure_launch_agent_loaded "$TUNNEL_LABEL" "$TUNNEL_PLIST"; then
    echo "Starting Cloudflare tunnel with launchd..."
    launchctl kickstart -k "$USER_DOMAIN/$TUNNEL_LABEL"
    sleep 3
    echo "Cloudflare tunnel is running with launchd."
    return
  fi

  local existing_pid
  existing_pid="$(read_pid_file "$TUNNEL_PID_FILE")"
  if [ -n "$existing_pid" ] && is_pid_running "$existing_pid"; then
    echo "Cloudflare tunnel already running (pid $existing_pid)."
    return
  fi

  echo "Starting Cloudflare tunnel..."
  nohup bash "$ROOT_DIR/scripts/run_cloudflare_public_tunnel.sh" >"$TUNNEL_LOG" 2>&1 &
  echo "$!" >"$TUNNEL_PID_FILE"
  sleep 3

  local tunnel_pid
  tunnel_pid="$(read_pid_file "$TUNNEL_PID_FILE")"
  if ! is_pid_running "$tunnel_pid"; then
    echo "Cloudflare tunnel failed to start."
    echo "Recent tunnel log:"
    tail -n 40 "$TUNNEL_LOG" || true
    exit 1
  fi

  echo "Cloudflare tunnel is running."
}

start_backend
start_tunnel

if wait_for_url "$PUBLIC_HEALTH_URL" 20; then
  public_status="ok"
else
  public_status="unreachable"
fi

echo
echo "Bunny public service is ready."
echo "Public URL: $PUBLIC_URL"
echo "Public health: $public_status ($PUBLIC_HEALTH_URL)"
echo "Backend log: $BACKEND_LOG"
echo "Tunnel log: $TUNNEL_LOG"
