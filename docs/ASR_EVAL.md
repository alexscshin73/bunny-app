# ASR Evaluation Workflow

Use this workflow when ASR quality feels unstable and you want to compare models or decoding settings with the same WAV sample set.

## Goal

- collect a small Korean and Spanish sample set
- define expected transcript text for each file
- run the same files through one or more Whisper models
- compare similarity, language match, and empty or unknown outputs

## Suggested Sample Set

Start with 20 to 40 short clips:

- 10 Korean everyday sentences
- 10 Spanish everyday sentences
- 5 mixed or noisy Korean clips
- 5 mixed or noisy Spanish clips

Keep clips short and realistic:

- 1 to 6 seconds each
- 16-bit mono WAV
- room noise similar to the real demo

Recommended layout:

```text
eval-audio/
  ko/
    check_01.wav
    check_02.wav
  es/
    check_01.wav
    check_02.wav
```

## Expected Manifest

Create a JSON file that maps each WAV to its expected language and transcript.

Example: [`asr_eval_expected.sample.json`](/Users/sclshin/Projects/bunny-app/docs/asr_eval_expected.sample.json)

Fastest way to bootstrap a real manifest from your current WAV files:

```bash
../bunny2/.venv/bin/python scripts/init_asr_expected.py eval-audio --output docs/asr_eval_expected.json
```

This will:

- scan `eval-audio/` recursively
- create one entry per WAV file
- infer `language` from the first folder name when it is `ko` or `es`
- preserve existing `text` values unless `--force` is used

Then fill in each `text` field with the expected transcript.

Supported keys:

- file name only: `check_01.wav`
- relative path: `ko/check_01.wav`

Relative paths are safer when the same file names are reused across languages.

## Commands

Fastest path with local defaults:

```bash
bash scripts/run_asr_eval.sh
```

This wrapper:

- reads clips from `eval-audio/`
- uses `docs/asr_eval_expected.sample.json` by default
- compares any available local Whisper models it finds
- saves a timestamped JSON report under `eval-reports/`

Use the current runtime model:

```bash
../bunny2/.venv/bin/python scripts/eval_wav.py eval-audio --expected docs/asr_eval_expected.json --summary
```

Run ASR only:

```bash
../bunny2/.venv/bin/python scripts/eval_wav.py eval-audio --expected docs/asr_eval_expected.sample.json --summary --no-translate
```

Compare multiple models:

```bash
../bunny2/.venv/bin/python scripts/eval_wav.py eval-audio \
  --expected docs/asr_eval_expected.json \
  --model-path ../bunny2/models/whisper/ggml-large-v3-turbo.bin \
  --model-path ../bunny2/models/whisper/ggml-large-v3.bin \
  --summary
```

Wrapper options use env vars:

```bash
ASR_EVAL_NO_TRANSLATE=1 bash scripts/run_asr_eval.sh
ASR_EVAL_JSON=1 bash scripts/run_asr_eval.sh
ASR_EVAL_USE_GPU=1 bash scripts/run_asr_eval.sh
```

To force a specific output file:

```bash
ASR_EVAL_OUTPUT=eval-reports/baseline-turbo.json bash scripts/run_asr_eval.sh
```

Saved report structure:

- `metadata`: when and how the evaluation was run
- `reports`: per-file results
- `summary`: aggregate metrics by model when `--summary` is enabled

## Compare Two Saved Reports

After you produce a baseline and a candidate report, compare them directly:

```bash
../bunny2/.venv/bin/python scripts/compare_asr_reports.py \
  eval-reports/baseline.json \
  eval-reports/candidate.json
```

JSON output:

```bash
../bunny2/.venv/bin/python scripts/compare_asr_reports.py \
  eval-reports/baseline.json \
  eval-reports/candidate.json \
  --json
```

This comparison shows:

- per-file winner
- score delta between baseline and candidate
- baseline and candidate transcript text side by side

Fastest path for the newest two reports:

```bash
bash scripts/compare_latest_asr_reports.sh
```

JSON output for later analysis:

```bash
../bunny2/.venv/bin/python scripts/eval_wav.py eval-audio \
  --expected docs/asr_eval_expected.sample.json \
  --summary \
  --json
```

## Reading The Summary

Important fields:

- `avg_similarity`: transcript similarity to the expected text
- `language_match_rate`: how often detected language matched the expected language
- `contains_rate`: whether one string mostly contains the other
- `unknown_count`: outputs that came back as `unknown`
- `empty_text_count`: clips that produced no transcript

## Decision Rule

Use the evaluation results to decide:

- keep `large-v3-turbo` if latency matters most and quality is acceptable
- move to `large-v3` if hallucinations or Korean accuracy are still too weak
- tune VAD and decode thresholds only after you have a stable baseline report
