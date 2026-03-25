# Real Two-User Demo

This checklist is for the real target scenario: two people actually speak in Korean and Spanish and both see translated captions.

## Goal

- speaker A joins as Korean
- speaker B joins as Spanish
- both use the same room on two browsers or two laptops/phones
- each speaker talks in turn
- the UI shows the original speech plus the translated counterpart

## Before the Demo

1. Start the backend in real runtime mode:
   - `bash scripts/run_real_demo.sh`
2. Open [`/healthz`](http://127.0.0.1:8000/healthz)
3. Confirm:
   - `asr.engine` is `whisper_cpp`
   - `asr.ready` is `true`
   - `translation.engine` is `nllb_ct2`
   - `translation.ready` is `true`
   - `speech_runtime.segment_emit_ms` is `800`
   - `speech_runtime.vad_silence_ms` is `550`
4. Open `http://127.0.0.1:8000/` on two browsers or devices.
5. On the first browser:
   - enter a Korean speaker name
   - choose `Korean`
   - click `Create Room`
   - click `Copy Invite Link`
6. On the second browser:
   - open the invite link
   - enter a Spanish speaker name
   - choose `Spanish`
   - click `Join Room`

## During the Demo

1. Speaker A clicks `Start Mic`
2. Speaker A says one short sentence in Korean
3. Speaker A clicks `Stop Mic`
4. Verify:
   - live caption appeared
   - a final conversation turn was added
   - the Spanish translation is visible
5. Speaker B repeats the same flow in Spanish
6. Verify:
   - the next turn is appended
   - the Korean translation is visible

## 2-Minute Script

Use this if one person is presenting and two people are holding the devices.

1. Presenter:
   - "We are now opening the same Bunny room on two browsers."
2. Korean speaker:
   - create the room
   - copy the invite link
3. Spanish speaker:
   - open the invite link
   - confirm the suggested join language is Spanish
   - join the room
4. Presenter:
   - "Both participants are now in the same room. Each person speaks in their own language, and the other language appears immediately."
5. Korean speaker:
   - click `Start Mic`
   - say: `안녕하세요, 오늘 일정 괜찮으세요?`
   - click `Stop Mic`
6. Presenter:
   - "The original Korean is shown first, and the Spanish translation is shown under it."
7. Spanish speaker:
   - click `Start Mic`
   - say: `Si, estoy listo. Podemos empezar ahora.`
   - click `Stop Mic`
8. Presenter:
   - "Now the Spanish original is shown together with the Korean translation. This is the core two-person conversation flow."

## Pass Criteria

- both participants appear in the room header
- live caption updates while speaking
- final turns accumulate in history
- each final turn shows original plus translated text
- no participant needs to type demo text manually

## Speaking Tips

- keep each turn to one or two short sentences
- wait for the live caption to settle before the next speaker starts
- in a noisy room, move closer to the microphone before increasing turn length

## If It Falls Back To Mock

- the web setup panel will show `ASR mock` or `Translation mock`
- this means the current backend is not in real speech mode
- stop the server and restart with `bash scripts/run_real_demo.sh`

## Troubleshooting

- If the second browser cannot join:
  - confirm the room code is correct
  - confirm the room preview does not say `Room Full`
- If one speaker cannot start the mic:
  - wait until the other speaker presses `Stop Mic`
  - refresh the page once if the socket was just reconnected
- If captions feel delayed:
  - shorten each turn to one sentence
  - reduce background noise
- If the health panel shows `Backend unavailable`:
  - restart with `bash scripts/run_real_demo.sh`
