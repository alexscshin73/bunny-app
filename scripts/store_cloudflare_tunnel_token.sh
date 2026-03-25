#!/usr/bin/env bash

set -euo pipefail

KEYCHAIN_SERVICE="${BUNNY_CLOUDFLARE_KEYCHAIN_SERVICE:-bunny-app-cloudflare-tunnel}"
KEYCHAIN_ACCOUNT="${BUNNY_CLOUDFLARE_KEYCHAIN_ACCOUNT:-bunny.carroamix.com}"
TOKEN="${1:-}"

if [ -z "$TOKEN" ]; then
  printf "Paste the refreshed Cloudflare tunnel token: "
  read -r TOKEN
fi

if [ -z "$TOKEN" ]; then
  echo "A non-empty token is required."
  exit 1
fi

security add-generic-password \
  -U \
  -a "$KEYCHAIN_ACCOUNT" \
  -s "$KEYCHAIN_SERVICE" \
  -w "$TOKEN"

echo "Stored Cloudflare tunnel token in Keychain."
echo "Service: $KEYCHAIN_SERVICE"
echo "Account: $KEYCHAIN_ACCOUNT"
