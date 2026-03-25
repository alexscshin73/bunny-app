# bunny-app

## Live Service

- Open Bunny now: https://bunny.carroamix.com
- Browser room client: https://bunny.carroamix.com/

`bunny-app` is a new service layer built by copying the reusable MVP pieces from `bunny2` while keeping `bunny2` intact.

## Product Goal

Build a real-time conversation app for Korean and Mexican users.

Core scenario:

1. A Korean user and a Mexican user join the same conversation room.
2. They talk in real time through the app.
3. The app listens to speech, recognizes text, and shows translated captions immediately.
4. In version 2, the translated result is also played back as speech.

## What We Reuse From `bunny2`

`bunny2` already provides the most important backend MVP pieces:

- WebSocket-based real-time audio streaming
- Streaming ASR pipeline
- Korean-Spanish translation pipeline
- Session/event model for partial and final transcript updates
- Swap-friendly translation backend structure

Copied into this repo:

- FastAPI app skeleton
- WebSocket realtime audio route
- ASR/translation pipeline services
- test scaffolding
- local debug web client

This means `bunny-app` can evolve independently without changing the original `bunny2` folder.
The fastest path is:

- Keep `bunny2` as the translation engine server
- Build `bunny-app` as the mobile client and conversation product layer
- Grow a separate backend surface here for rooms, participants, and app-facing APIs

## Demo Status

There are now two clearly different demo modes in this repo:

- `presentation mode`: one-device mobile walkthrough using demo turns and local TTS
- `real conversation mode`: two actual speakers join the same room in the browser and speak in turn

If the goal is a true conversation demo with two humans speaking, the browser room client is the primary path today.

## Current Repo Scope

`bunny-app` now contains:

- copied realtime translation backend code from `bunny2`
- a lightweight room API scaffold at `/api/rooms`
- the original WebSocket translation endpoint at `/ws/audio`
- a room-aware realtime WebSocket endpoint at `/ws/rooms/{room_id}?participant_id=...`
- SQLite-backed room and turn persistence by default
- a room-based browser client for real two-user speech demos
- an Expo-based mobile scaffold in [`mobile/`](/Users/sclshin/Projects/bunny-app/mobile)

## Real Two-User Demo

Use this path when you want the product outcome, not a scripted walkthrough.

Prerequisites already available on this machine:

- `whisper-cli` is installed
- `bunny2` contains local Whisper and NLLB model files

Recommended start command:

1. `bash scripts/run_real_demo.sh`
2. open `http://127.0.0.1:8000/healthz`
3. confirm `asr.engine=whisper_cpp` and `translation.engine=nllb_ct2`
4. confirm `speech_runtime.segment_emit_ms=800` and `speech_runtime.vad_silence_ms=550`
5. open `http://127.0.0.1:8000/` on two browsers or two devices
6. first speaker creates the room and shares the invite link
7. second speaker joins the same room
8. each speaker talks in turn using `Start Mic` and `Stop Mic`

Related files:

- real runtime env example: [`.env.real-demo.example`](/Users/sclshin/Projects/bunny-app/.env.real-demo.example)
- launcher script: [`scripts/run_real_demo.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_real_demo.sh)
- local multi-project policy: [`docs/LOCAL_MULTI_PROJECT_DEV.md`](/Users/sclshin/Projects/bunny-app/docs/LOCAL_MULTI_PROJECT_DEV.md)
- public Cloudflare tunnel guide: [`docs/CLOUDFLARE_TUNNEL.md`](/Users/sclshin/Projects/bunny-app/docs/CLOUDFLARE_TUNNEL.md)
- carroamix hostname checklist: [`docs/BUNNY_CARROAMIX_SETUP.md`](/Users/sclshin/Projects/bunny-app/docs/BUNNY_CARROAMIX_SETUP.md)
- named tunnel runner: [`scripts/run_cloudflare_public_tunnel.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_cloudflare_public_tunnel.sh)
- macOS launcher guide: [`docs/MAC_PUBLIC_LAUNCHER.md`](/Users/sclshin/Projects/bunny-app/docs/MAC_PUBLIC_LAUNCHER.md)
- macOS auto start guide: [`docs/MAC_AUTOSTART.md`](/Users/sclshin/Projects/bunny-app/docs/MAC_AUTOSTART.md)
- token storage helper: [`scripts/store_cloudflare_tunnel_token.sh`](/Users/sclshin/Projects/bunny-app/scripts/store_cloudflare_tunnel_token.sh)
- public start helper: [`scripts/bunny_public_start.sh`](/Users/sclshin/Projects/bunny-app/scripts/bunny_public_start.sh)
- public stop helper: [`scripts/bunny_public_stop.sh`](/Users/sclshin/Projects/bunny-app/scripts/bunny_public_stop.sh)
- public status helper: [`scripts/bunny_public_status.sh`](/Users/sclshin/Projects/bunny-app/scripts/bunny_public_status.sh)
- step-by-step checklist: [`docs/REAL_TWO_USER_DEMO.md`](/Users/sclshin/Projects/bunny-app/docs/REAL_TWO_USER_DEMO.md)
- presenter-friendly 2-minute script and troubleshooting: [`docs/REAL_TWO_USER_DEMO.md`](/Users/sclshin/Projects/bunny-app/docs/REAL_TWO_USER_DEMO.md)

## ASR Evaluation

Use this path when speech quality needs to be compared across models or decoding settings.

Recommended flow:

1. collect a small WAV sample set under `eval-audio/`
2. create an expected transcript manifest
3. run `scripts/eval_wav.py` against one or more model files
4. compare summary metrics before changing the live runtime default

Related files:

- evaluator script: [`scripts/eval_wav.py`](/Users/sclshin/Projects/bunny-app/scripts/eval_wav.py)
- manifest bootstrapper: [`scripts/init_asr_expected.py`](/Users/sclshin/Projects/bunny-app/scripts/init_asr_expected.py)
- quick runner: [`scripts/run_asr_eval.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_asr_eval.sh)
- saved-report comparer: [`scripts/compare_asr_reports.py`](/Users/sclshin/Projects/bunny-app/scripts/compare_asr_reports.py)
- latest-report comparer: [`scripts/compare_latest_asr_reports.sh`](/Users/sclshin/Projects/bunny-app/scripts/compare_latest_asr_reports.sh)
- evaluation workflow: [`docs/ASR_EVAL.md`](/Users/sclshin/Projects/bunny-app/docs/ASR_EVAL.md)
- sample expected manifest: [`docs/asr_eval_expected.sample.json`](/Users/sclshin/Projects/bunny-app/docs/asr_eval_expected.sample.json)
- starter audio folders: [`eval-audio/ko`](/Users/sclshin/Projects/bunny-app/eval-audio/ko), [`eval-audio/es`](/Users/sclshin/Projects/bunny-app/eval-audio/es)
- saved reports: [`eval-reports/`](/Users/sclshin/Projects/bunny-app/eval-reports)

## Room API

Initial endpoints:

- `POST /api/rooms`
- `GET /api/rooms`
- `GET /api/rooms/{room_id}`
- `POST /api/rooms/{room_id}/join`

Current rules:

- maximum 2 participants per room
- `ko` and `es` are the only supported languages
- duplicate language joins are rejected
- room and turn history persist in SQLite unless `BUNNY_ROOM_STORE_BACKEND=memory`

## Storage

Default backend:

- `BUNNY_ROOM_STORE_BACKEND=sqlite`
- `BUNNY_ROOM_STORE_PATH=data/bunny_app.sqlite3`
- `BUNNY_ROOM_STORE_URL=postgresql://postgres:postgres@127.0.0.1:5432/bunny_app`
- `BUNNY_ROOM_TTL_MINUTES=1440`
- `BUNNY_ROOM_CLEANUP_INTERVAL_SECONDS=300`

Useful for tests or fully ephemeral runs:

- `BUNNY_ROOM_STORE_BACKEND=memory`

Postgres option:

- set `BUNNY_ROOM_STORE_BACKEND=postgres`
- set `BUNNY_ROOM_STORE_URL` to your database DSN
- install the optional driver with `pip install .[postgres]`

Local Postgres for smoke testing:

1. `docker compose -f docker-compose.postgres.yml up -d --build`
2. open `http://127.0.0.1:8000/healthz`
3. `export BUNNY_ROOM_STORE_BACKEND=postgres`
4. `export BUNNY_ROOM_STORE_URL=postgresql://postgres:postgres@127.0.0.1:5432/bunny_app`
5. `export BUNNY_TEST_POSTGRES_URL=$BUNNY_ROOM_STORE_URL`
6. `pytest tests/test_postgres_store_integration.py`

Local stack notes:

- [`docker-compose.postgres.yml`](/Users/sclshin/Projects/bunny-app/docker-compose.postgres.yml) starts both Postgres and the FastAPI app
- [`Dockerfile`](/Users/sclshin/Projects/bunny-app/Dockerfile) installs the optional Postgres driver and runs `uvicorn`
- the containerized app uses `mock` ASR/translation by default so the stack comes up without local model files
- for a real two-speaker speech demo, use the host runtime with [`scripts/run_real_demo.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_real_demo.sh) instead of the default Docker stack
- the mobile app can target this stack through `EXPO_PUBLIC_BUNNY_BACKEND_URL=http://127.0.0.1:8000` or by editing the backend URL field in-app

Cleanup behavior:

- rooms are pruned automatically when `last_activity_at` is older than the configured TTL
- a background cleanup loop also removes expired rooms on a fixed interval
- activity is refreshed when participants join or finalized turns are stored
- `POST /api/rooms/_cleanup` can be used to trigger cleanup manually

## Recommended V1 Scope

Version 1 should focus on text-first live translation.

### User Experience

- Two users enter the same room
- Each user selects their language: `ko` or `es`
- The app captures microphone audio
- Audio is streamed to the `bunny2` backend over WebSocket
- The app receives:
  - partial transcript
  - final transcript
  - translated text
- The conversation screen shows both:
  - original speech text
  - translated text for the other participant

### Why This Scope

This delivers the core value quickly:

- real conversation
- immediate understanding
- reusable `bunny2` backend
- lower implementation risk than voice playback

## Recommended V2 Scope

Version 2 adds spoken translation output.

### Added Experience

- After translation is finalized, generate TTS audio in the listener's language
- Play translated speech automatically or with a tap-to-play interaction
- Add playback controls and mute/autoplay preferences

### Important Constraint

V2 should use finalized translations for speech output first.
Trying to speak every partial translation in real time will feel unstable and noisy.

## Suggested Architecture

### 1. Mobile App (`bunny-app`)

Responsibilities:

- sign-in or guest entry
- room join/create flow
- microphone permission and audio capture
- WebSocket connection management
- conversation UI
- participant state
- translated caption rendering
- later TTS playback UI

Recommended stack:

- React Native with Expo, or
- React Native bare workflow if lower-level audio control becomes necessary

### 2. Realtime Translation Server (`bunny2`)

Responsibilities:

- receive PCM audio chunks
- run ASR
- detect source language when possible
- translate into target language
- return partial/final events

### 3. Room/Session Layer

This can live either:

- inside `bunny-app` backend later, or
- as a thin API in front of `bunny2`

Responsibilities:

- create room IDs
- map participant A/B languages
- issue session tokens
- connect app users to the correct realtime stream

For the first MVP, even a very simple room model is enough.

## Event Flow

Recommended V1 flow:

1. User enters a room
2. User chooses `ko` or `es`
3. App opens a WebSocket session
4. App sends `start` with sample rate and language
5. App streams microphone PCM chunks
6. Backend emits:
   - `ready`
   - `session_started`
   - `partial`
   - `translation`
   - `final`
   - `stats`
7. App renders the current live turn and stores finalized conversation items

## MVP Data Model

Minimal entities:

- `User`
  - `id`
  - `displayName`
  - `language`
- `Room`
  - `id`
  - `status`
  - `participants`
- `ConversationTurn`
  - `id`
  - `speakerId`
  - `sourceLanguage`
  - `sourceText`
  - `translatedText`
  - `isFinal`
  - `createdAt`

## Product Rules

- V1 supports only `ko <-> es`
- One room is limited to two active speakers
- Show source text and translation together
- Final text is stored in conversation history
- Partial text is shown as temporary UI state
- V2 TTS should speak only stable final translations by default

## Build Order

### Phase 1

- Define mobile app structure
- Implement room entry screen
- Implement conversation screen shell
- Connect to `bunny2` WebSocket with mock/local backend

### Phase 2

- Stream microphone audio from mobile
- Render partial/final transcript and translated text
- Stabilize reconnect/error handling

### Phase 3

- Add room state and participant presence
- Add conversation history persistence if needed
- Prepare TTS interface for V2

### Phase 4

- Add translated voice playback
- Add autoplay/mute controls
- Optimize latency and speech quality

## Practical Recommendation

The most realistic way to show the real product today is:

1. run the backend in real runtime mode with `whisper.cpp` and `nllb_ct2`
2. use the browser room client for the live two-user conversation demo
3. treat the mobile app as a secondary client for product exploration and follow-up polishing
4. keep translated voice playback as a later enhancement after the live caption experience is stable

This keeps the demo aligned with the actual goal: two people talking and seeing translated captions in real time.

## Next Step

The next implementation target should be one of these:

1. Add native microphone capture and PCM chunk streaming from `mobile/`
2. Persist room and conversation history outside in-memory storage
3. Add finalized-translation TTS playback for V2

## Mobile App

`mobile/` is the new Expo client scaffold for Bunny App.

It currently supports:

- backend URL input for local device testing
- room create and join flows
- realtime room socket connection
- participant presence UI
- live translation event rendering
- web microphone PCM streaming
- native microphone permission and local recording state
- native recorded-turn upload translation
- on-device translated voice playback
- debug controls for `ping`

The next mobile milestone is native PCM chunk streaming into `/ws/rooms/{room_id}` through either a custom native bridge, bare React Native audio module, or WebRTC-based transport.
