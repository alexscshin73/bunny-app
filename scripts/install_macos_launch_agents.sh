#!/usr/bin/env bash

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer only works on macOS."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT_DIR/run"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
USER_DOMAIN="gui/$(id -u)"

BACKEND_LABEL="com.sclshin.bunny.backend"
TUNNEL_LABEL="com.sclshin.bunny.tunnel"
BACKEND_TEMPLATE="$ROOT_DIR/macos/launchd/$BACKEND_LABEL.plist.template"
TUNNEL_TEMPLATE="$ROOT_DIR/macos/launchd/$TUNNEL_LABEL.plist.template"
BACKEND_PLIST="$LAUNCH_AGENTS_DIR/$BACKEND_LABEL.plist"
TUNNEL_PLIST="$LAUNCH_AGENTS_DIR/$TUNNEL_LABEL.plist"

render_template() {
  local template_path="$1"
  local output_path="$2"

  sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$template_path" > "$output_path"
}

bootout_if_loaded() {
  local plist_path="$1"
  launchctl bootout "$USER_DOMAIN" "$plist_path" >/dev/null 2>&1 || true
}

mkdir -p "$RUN_DIR" "$LAUNCH_AGENTS_DIR"

render_template "$BACKEND_TEMPLATE" "$BACKEND_PLIST"
render_template "$TUNNEL_TEMPLATE" "$TUNNEL_PLIST"

plutil -lint "$BACKEND_PLIST" >/dev/null
plutil -lint "$TUNNEL_PLIST" >/dev/null

bootout_if_loaded "$BACKEND_PLIST"
bootout_if_loaded "$TUNNEL_PLIST"

launchctl bootstrap "$USER_DOMAIN" "$BACKEND_PLIST"
launchctl bootstrap "$USER_DOMAIN" "$TUNNEL_PLIST"
launchctl kickstart -k "$USER_DOMAIN/$BACKEND_LABEL"
launchctl kickstart -k "$USER_DOMAIN/$TUNNEL_LABEL"

echo "Installed launch agents:"
echo "  $BACKEND_PLIST"
echo "  $TUNNEL_PLIST"
echo
echo "They will now start automatically at login."
echo "Status:"
echo "  bash $ROOT_DIR/scripts/bunny_launchd_status.sh"
echo "Remove later:"
echo "  bash $ROOT_DIR/scripts/uninstall_macos_launch_agents.sh"
