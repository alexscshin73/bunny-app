#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOCAL_BIN_DIR="${HOME}/.local/bin"
WHISPER_SRC_DIR="${HOME}/.local/src/whisper.cpp"
PIP_BOOTSTRAP_URL="${BUNNY_PIP_BOOTSTRAP_URL:-https://bootstrap.pypa.io/get-pip.py}"
CLOUDFLARED_URL="${BUNNY_CLOUDFLARED_URL:-https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64}"

mkdir -p "$LOCAL_BIN_DIR" "${HOME}/.local/src"

install_pip_user() {
  if python3 -m pip --version >/dev/null 2>&1; then
    return 0
  fi

  local bootstrap_script
  bootstrap_script="$(mktemp)"
  curl -fsSL "$PIP_BOOTSTRAP_URL" -o "$bootstrap_script"
  python3 "$bootstrap_script" --user --break-system-packages
  rm -f "$bootstrap_script"
}

install_python_deps() {
  python3 -m pip install --user --break-system-packages ".[postgres]"
}

ensure_cmake_user() {
  if command -v cmake >/dev/null 2>&1; then
    return 0
  fi

  python3 -m pip install --user --break-system-packages cmake
}

install_cloudflared_user() {
  if [ -x "$LOCAL_BIN_DIR/cloudflared" ]; then
    return 0
  fi

  curl -fsSL "$CLOUDFLARED_URL" -o "$LOCAL_BIN_DIR/cloudflared"
  chmod +x "$LOCAL_BIN_DIR/cloudflared"
}

install_whisper_cli_user() {
  if [ -x "$LOCAL_BIN_DIR/whisper-cli" ]; then
    return 0
  fi

  export PATH="$LOCAL_BIN_DIR:$PATH"
  ensure_cmake_user

  rm -rf "$WHISPER_SRC_DIR"
  git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git "$WHISPER_SRC_DIR"
  make -C "$WHISPER_SRC_DIR" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)"

  if [ -x "$WHISPER_SRC_DIR/build/bin/whisper-cli" ]; then
    ln -sf "$WHISPER_SRC_DIR/build/bin/whisper-cli" "$LOCAL_BIN_DIR/whisper-cli"
    return 0
  fi

  if [ -x "$WHISPER_SRC_DIR/main" ]; then
    ln -sf "$WHISPER_SRC_DIR/main" "$LOCAL_BIN_DIR/whisper-cli"
    return 0
  fi

  echo "whisper-cli build completed, but no binary was found."
  exit 1
}

cd "$ROOT_DIR"
install_pip_user
install_python_deps
install_cloudflared_user
install_whisper_cli_user

echo "Playtica runtime install complete."
echo "pip: $(python3 -m pip --version)"
echo "cloudflared: $LOCAL_BIN_DIR/cloudflared"
echo "whisper-cli: $LOCAL_BIN_DIR/whisper-cli"
