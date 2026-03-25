#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUNNY2_DIR="${BUNNY2_DIR:-$(cd "$ROOT_DIR/../bunny2" && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-$BUNNY2_DIR/.venv/bin/python}"
REPORT_DIR="${ASR_EVAL_REPORT_DIR:-$ROOT_DIR/eval-reports}"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "python runtime was not found at $PYTHON_BIN"
  echo "Set PYTHON_BIN or prepare the bunny2 virtualenv first."
  exit 1
fi

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOF'
Usage: bash scripts/compare_latest_asr_reports.sh

Compares the newest two JSON files under eval-reports/ by default.

Environment flags:
- ASR_EVAL_REPORT_DIR=/path/to/eval-reports
EOF
  exit 0
fi

if [ ! -d "$REPORT_DIR" ]; then
  echo "report directory was not found at $REPORT_DIR"
  echo "Run bash scripts/run_asr_eval.sh first or set ASR_EVAL_REPORT_DIR."
  exit 1
fi

mapfile -t REPORTS < <(find "$REPORT_DIR" -maxdepth 1 -type f -name '*.json' | sort)

if [ "${#REPORTS[@]}" -lt 2 ]; then
  echo "need at least two report files in $REPORT_DIR"
  exit 1
fi

BASELINE="${REPORTS[-2]}"
CANDIDATE="${REPORTS[-1]}"

echo "Baseline: $BASELINE"
echo "Candidate: $CANDIDATE"

exec "$PYTHON_BIN" "$ROOT_DIR/scripts/compare_asr_reports.py" "$BASELINE" "$CANDIDATE"
