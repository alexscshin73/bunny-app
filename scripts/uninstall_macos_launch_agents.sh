#!/usr/bin/env bash

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This uninstaller only works on macOS."
  exit 1
fi

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
USER_DOMAIN="gui/$(id -u)"

BACKEND_LABEL="com.sclshin.bunny.backend"
TUNNEL_LABEL="com.sclshin.bunny.tunnel"
BACKEND_PLIST="$LAUNCH_AGENTS_DIR/$BACKEND_LABEL.plist"
TUNNEL_PLIST="$LAUNCH_AGENTS_DIR/$TUNNEL_LABEL.plist"

remove_agent() {
  local plist_path="$1"

  if [ -f "$plist_path" ]; then
    launchctl bootout "$USER_DOMAIN" "$plist_path" >/dev/null 2>&1 || true
    rm -f "$plist_path"
    echo "Removed $plist_path"
  else
    echo "Not installed: $plist_path"
  fi
}

remove_agent "$BACKEND_PLIST"
remove_agent "$TUNNEL_PLIST"
