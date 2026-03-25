#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUNNY2_DIR="${BUNNY2_DIR:-$(cd "$ROOT_DIR/../bunny2" && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-$BUNNY2_DIR/.venv/bin/python}"
DEFAULT_AUDIO_DIR="${ASR_EVAL_AUDIO_DIR:-$ROOT_DIR/eval-audio}"
DEFAULT_REPORT_DIR="${ASR_EVAL_REPORT_DIR:-$ROOT_DIR/eval-reports}"

if [ -n "${ASR_EVAL_EXPECTED_FILE:-}" ]; then
  DEFAULT_EXPECTED_FILE="$ASR_EVAL_EXPECTED_FILE"
elif [ -f "$ROOT_DIR/docs/asr_eval_expected.json" ]; then
  DEFAULT_EXPECTED_FILE="$ROOT_DIR/docs/asr_eval_expected.json"
else
  DEFAULT_EXPECTED_FILE="$ROOT_DIR/docs/asr_eval_expected.sample.json"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "python runtime was not found at $PYTHON_BIN"
  echo "Set PYTHON_BIN or prepare the bunny2 virtualenv first."
  exit 1
fi

if [ ! -d "$DEFAULT_AUDIO_DIR" ]; then
  echo "evaluation audio directory was not found at $DEFAULT_AUDIO_DIR"
  echo "Create eval-audio/ko and eval-audio/es or set ASR_EVAL_AUDIO_DIR first."
  exit 1
fi

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
Usage: bash scripts/run_asr_eval.sh [MODEL_PATH...]

Runs scripts/eval_wav.py against eval-audio/ with the default expected manifest.

If MODEL_PATH arguments are omitted, the script tries available local whisper models:
- ggml-large-v3-turbo.bin
- ggml-large-v3.bin
- ggml-small.bin

Environment flags:
- ASR_EVAL_AUDIO_DIR=/path/to/eval-audio
- ASR_EVAL_EXPECTED_FILE=/path/to/expected.json
- ASR_EVAL_REPORT_DIR=/path/to/eval-reports
- ASR_EVAL_OUTPUT=/path/to/report.json
- ASR_EVAL_NO_TRANSLATE=1
- ASR_EVAL_JSON=1
- ASR_EVAL_USE_GPU=1
EOF
  exit 0
fi

TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_PATH="${ASR_EVAL_OUTPUT:-$DEFAULT_REPORT_DIR/asr-eval-$TIMESTAMP.json}"

MODEL_PATHS=()

if [ "$#" -gt 0 ]; then
  for raw_model_path in "$@"; do
    MODEL_PATHS+=("$raw_model_path")
  done
else
  for candidate in \
    "$BUNNY2_DIR/models/whisper/ggml-large-v3-turbo.bin" \
    "$BUNNY2_DIR/models/whisper/ggml-large-v3.bin" \
    "$BUNNY2_DIR/models/whisper/ggml-small.bin"
  do
    if [ -f "$candidate" ]; then
      MODEL_PATHS+=("$candidate")
    fi
  done
fi

if [ "${#MODEL_PATHS[@]}" -eq 0 ]; then
  echo "no whisper model files were found"
  echo "Pass one or more model paths to scripts/run_asr_eval.sh"
  exit 1
fi

COMMAND=(
  "$PYTHON_BIN"
  "$ROOT_DIR/scripts/eval_wav.py"
  "$DEFAULT_AUDIO_DIR"
  "--expected" "$DEFAULT_EXPECTED_FILE"
  "--summary"
  "--output" "$REPORT_PATH"
)

if [ "${ASR_EVAL_NO_TRANSLATE:-0}" = "1" ]; then
  COMMAND+=("--no-translate")
fi

if [ "${ASR_EVAL_JSON:-0}" = "1" ]; then
  COMMAND+=("--json")
fi

if [ "${ASR_EVAL_USE_GPU:-0}" = "1" ]; then
  COMMAND+=("--use-gpu")
fi

for model_path in "${MODEL_PATHS[@]}"; do
  COMMAND+=("--model-path" "$model_path")
done

echo "Running ASR evaluation on: $DEFAULT_AUDIO_DIR"
echo "Expected manifest: $DEFAULT_EXPECTED_FILE"
echo "Report output: $REPORT_PATH"
printf 'Models:\n'
for model_path in "${MODEL_PATHS[@]}"; do
  echo " - $model_path"
done

exec "${COMMAND[@]}"
