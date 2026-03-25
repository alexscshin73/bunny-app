# Bunny App Mobile

This folder contains the Expo-based mobile scaffold for `bunny-app`.

## Included

- room creation and room join flow
- room-aware realtime WebSocket connection
- participant presence rendering
- live turn and finalized turn UI
- debug session controls for `start`, `stop`, and `ping`
- web microphone PCM streaming into the realtime room socket
- native microphone permission and local recorder state via `expo-audio`
- native recorded-turn upload to `/api/rooms/{room_id}/turns/upload`
- room history fetch and refresh via `/api/rooms/{room_id}/turns`
- translated voice playback with `expo-speech`
- one-device demo flow with demo guest injection and canned demo turns

## Not Included Yet

- native microphone PCM streaming
- background audio handling
- backend-generated TTS audio files

## Current Microphone Behavior

- Web: captures microphone input and streams PCM16 chunks to `WS /ws/rooms/{room_id}`
- iOS/Android Expo managed runtime: requests mic permission, records locally, then uploads the recorded turn for server-side ASR and translation

That native limitation comes from the current official `expo-audio` surface, which exposes recorder preparation, recording, permissions, status, and output files, but not recorder-side realtime PCM sample callbacks.

The current fallback path is still useful for MVP testing because each recorded turn is translated by the backend and rebroadcast into the room event stream.

## Current TTS Behavior

- final translated turns can be played manually from conversation history
- autoplay can read incoming translated turns in the listener's language
- playback uses on-device/browser TTS, not backend audio generation
- users can switch Korean and Spanish voices when available on the device
- users can change TTS playback speed between slow, normal, and fast
- autoplay, speed, and selected voices persist across app restarts

## Setup

1. Install dependencies:

```bash
cd mobile
npm install
```

2. Start the Expo dev server:

```bash
npm run start
```

3. Configure the backend URL for your environment:

```bash
cp .env.example .env
```

Then set `EXPO_PUBLIC_BUNNY_BACKEND_URL` as needed:

- iOS simulator / web with local backend: `http://127.0.0.1:8000`
- Android emulator with local backend: `http://10.0.2.2:8000`
- real device on the same network: `http://192.168.x.x:8000`

4. You can still override the backend URL in the app UI before joining a room. For a real device, use your local network IP such as:

```text
http://192.168.x.x:8000
```

The app also keeps the last backend URL in local storage, so you do not need to re-enter it every time.
The join screen also checks `GET /healthz` automatically so you can verify the backend URL before entering a room.

Inside a room, the `Demo lab` panel can:

- add a second demo participant when you only have one device
- send canned Korean or Spanish sample turns without using the microphone
- run a one-tap bilingual scripted sequence for a fast walkthrough
- drive translation, room history, and TTS playback for fast QA and demos

The conversation screen also includes a `Demo readiness` panel so you can quickly judge:

- whether the room socket is connected
- whether two speakers are present
- whether finalized history exists
- whether device TTS voices are available

5. If you want to hit the Docker stack from the repo root, start it first:

```bash
docker compose -f ../docker-compose.postgres.yml up -d --build
```

## Expected Backend

Run the Python backend from the repo root:

```bash
uvicorn app.main:app --reload
```

The mobile app expects:

- `POST /api/rooms`
- `POST /api/rooms/{room_id}/join`
- `GET /api/rooms/{room_id}`
- `POST /api/rooms/{room_id}/turns/upload`
- `WS /ws/rooms/{room_id}?participant_id=...`

With the Docker stack, the default mock backend will be available on `http://127.0.0.1:8000`.

## Server Note

For native recorded uploads such as `.m4a`, the Python backend should have `ffmpeg` available so it can convert uploaded audio into 16 kHz mono PCM before ASR.
