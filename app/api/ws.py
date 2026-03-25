import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.config import get_settings
from app.models.events import ClientControlEvent
from app.models.rooms import RoomParticipant
from app.services.live_rooms import get_live_room_manager
from app.services.pipeline import build_asr, build_realtime_session, build_translator
from app.services.rooms import RoomNotFoundError, get_room_store

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


async def _send_events_if_connected(websocket: WebSocket, events: list) -> None:
    if websocket.client_state != WebSocketState.CONNECTED:
        return

    for event in events:
        try:
            await websocket.send_json(event.model_dump())
        except RuntimeError:
            return


def _participant_payload(participant: RoomParticipant) -> dict[str, str]:
    return {
        "participant_id": participant.participant_id,
        "display_name": participant.display_name,
        "icon": participant.icon,
        "language": participant.language,
    }


def _room_event_payload(
    room_id: str,
    participant: RoomParticipant,
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        **payload,
        "room_id": room_id,
        "speaker": _participant_payload(participant),
    }


async def _dispatch_room_events(
    websocket: WebSocket,
    room_id: str,
    participant: RoomParticipant,
    events: list,
    room_store,
) -> None:
    live_rooms = get_live_room_manager()
    for event in events:
        payload = _room_event_payload(room_id, participant, event.payload)
        if event.type == "translation" and payload.get("is_final"):
            turn = room_store.add_turn(
                room_id=room_id,
                participant=participant,
                source_language=str(payload.get("source_language", participant.language)),
                source_text=str(payload.get("source_text", "")),
                translations=dict(payload.get("translations", {})),
                delivery="realtime",
            )
            payload["turn_id"] = turn.turn_id
        message = {
            "type": event.type,
            "payload": payload,
        }
        if event.type in {"partial", "final", "translation"}:
            await live_rooms.broadcast(room_id, message)
            continue
        await live_rooms.send_json(websocket, message)


async def _broadcast_speaker_state(
    room_id: str,
    participant: RoomParticipant,
    *,
    active: bool,
    language: str,
    sample_rate: int | None = None,
) -> None:
    live_rooms = get_live_room_manager()
    payload: dict[str, object] = {
        "room_id": room_id,
        "speaker": _participant_payload(participant),
        "active": active,
        "language": language,
    }
    if sample_rate is not None:
        payload["sample_rate"] = sample_rate
    await live_rooms.broadcast(room_id, {"type": "speaker_state", "payload": payload})


@router.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    received_audio_chunks = 0

    settings = get_settings()
    asr = build_asr(settings)
    translator = build_translator(settings)
    session = build_realtime_session(settings)
    await websocket.send_json(
        {
            "type": "ready",
            "payload": {
                "targets": settings.translation_targets,
                "asr": asr.status().model_dump(),
                "translation": translator.status().model_dump(),
            },
        }
    )

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if message.get("bytes") is not None:
                received_audio_chunks += 1
                if received_audio_chunks == 1:
                    logger.info("ws/audio first audio chunk received: %s bytes", len(message["bytes"]))
                events = await session.push_audio(message["bytes"])
                await _send_events_if_connected(websocket, events)
                continue

            text = message.get("text")
            if text is None:
                continue

            control = ClientControlEvent.model_validate_json(text)
            logger.info("ws/audio control received: %s", control.type)
            events = await session.handle_control(control)
            await _send_events_if_connected(websocket, events)
    except WebSocketDisconnect:
        logger.info("ws/audio disconnected after %s audio chunks", received_audio_chunks)
        pass
    except Exception as exc:
        logger.exception("ws/audio failed after %s audio chunks", received_audio_chunks)
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(
                {"type": "error", "payload": {"message": str(exc)}}
            )
    finally:
        events = await session.close()
        await _send_events_if_connected(websocket, events)


@router.websocket("/ws/rooms/{room_id}")
async def room_audio_stream(websocket: WebSocket, room_id: str, participant_id: str) -> None:
    settings = get_settings()
    room_store = get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )

    try:
        room = room_store.get_room(room_id)
        participant = room_store.get_participant(room_id, participant_id)
    except RoomNotFoundError:
        await websocket.close(code=4404)
        return

    session = build_realtime_session(settings)
    live_rooms = get_live_room_manager()

    await websocket.accept()

    await live_rooms.connect(
        room_id=room_id,
        participant=participant,
        websocket=websocket,
        session=session,
    )

    await live_rooms.send_json(
        websocket,
        {
            "type": "room_ready",
            "payload": {
                "room_id": room_id,
                "participant": _participant_payload(participant),
                "participants": [_participant_payload(item) for item in room.participants],
                "targets": settings.translation_targets,
                "asr": session.asr.status().model_dump(),
                "translation": session.translator.status().model_dump(),
            },
        },
    )
    await live_rooms.broadcast(
        room_id,
        {
            "type": "participant_joined",
            "payload": {
                "room_id": room_id,
                "participant": _participant_payload(participant),
            },
        },
        exclude_participant_ids={participant.participant_id},
    )

    received_audio_chunks = 0
    speaker_active = False
    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if message.get("bytes") is not None:
                received_audio_chunks += 1
                if received_audio_chunks == 1:
                    logger.info(
                        "ws/rooms first audio chunk room=%s participant=%s bytes=%s",
                        room_id,
                        participant.participant_id,
                        len(message["bytes"]),
                    )
                events = await session.push_audio(message["bytes"])
                await _dispatch_room_events(websocket, room_id, participant, events, room_store)
                continue

            text = message.get("text")
            if text is None:
                continue

            control = ClientControlEvent.model_validate_json(text)
            logger.info(
                "ws/rooms control received room=%s participant=%s type=%s",
                room_id,
                participant.participant_id,
                control.type,
            )
            events = await session.handle_control(control)
            await _dispatch_room_events(websocket, room_id, participant, events, room_store)
            if control.type == "start":
                speaker_active = True
                await _broadcast_speaker_state(
                    room_id,
                    participant,
                    active=True,
                    language=session.language,
                    sample_rate=session.sample_rate,
                )
            elif control.type == "stop" and speaker_active:
                speaker_active = False
                await _broadcast_speaker_state(
                    room_id,
                    participant,
                    active=False,
                    language=session.language,
                )
    except WebSocketDisconnect:
        logger.info(
            "ws/rooms disconnected room=%s participant=%s audio_chunks=%s",
            room_id,
            participant.participant_id,
            received_audio_chunks,
        )
    except Exception as exc:
        logger.exception(
            "ws/rooms failed room=%s participant=%s audio_chunks=%s",
            room_id,
            participant.participant_id,
            received_audio_chunks,
        )
        await live_rooms.send_json(
            websocket,
            {"type": "error", "payload": {"message": str(exc)}},
        )
    finally:
        events = await session.close()
        await _dispatch_room_events(websocket, room_id, participant, events, room_store)
        if speaker_active:
            await _broadcast_speaker_state(
                room_id,
                participant,
                active=False,
                language=session.language,
            )
        live_rooms.disconnect(room_id, participant.participant_id, websocket=websocket)
        await live_rooms.broadcast(
            room_id,
            {
                "type": "participant_left",
                "payload": {
                    "room_id": room_id,
                    "participant": _participant_payload(participant),
                },
            },
        )
