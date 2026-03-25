#!/usr/bin/env bash

set -euo pipefail

KEYCHAIN_SERVICE="${BUNNY_CLOUDFLARE_KEYCHAIN_SERVICE:-bunny-app-cloudflare-tunnel}"
KEYCHAIN_ACCOUNT="${BUNNY_CLOUDFLARE_KEYCHAIN_ACCOUNT:-bunny.carroamix.com}"

load_token_from_keychain() {
  security find-generic-password -w -s "$KEYCHAIN_SERVICE" -a "$KEYCHAIN_ACCOUNT" 2>/dev/null || true
}

TOKEN="${BUNNY_CLOUDFLARE_TUNNEL_TOKEN:-$(load_token_from_keychain)}"

if [ -z "$TOKEN" ]; then
  echo "No Cloudflare tunnel token was found."
  echo
  echo "Store the token in the macOS Keychain or export it in your shell:"
  echo "  bash scripts/store_cloudflare_tunnel_token.sh '...'"
  echo "  export BUNNY_CLOUDFLARE_TUNNEL_TOKEN='...'"
  echo
  echo "See docs/CLOUDFLARE_TUNNEL.md for the full setup flow."
  exit 1
fi

echo "Starting Cloudflare named tunnel for bunny-app"
exec cloudflared tunnel run --token "$TOKEN"
