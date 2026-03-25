import io
import os
import wave

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.services.live_rooms import get_live_room_manager
from app.services.rooms import get_room_store


def make_mock_client() -> TestClient:
    os.environ["BUNNY_ASR_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_TARGETS"] = "[\"ko\",\"es\"]"
    os.environ["BUNNY_VAD_ENABLED"] = "false"
    os.environ["BUNNY_ROOM_STORE_BACKEND"] = "memory"
    os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"
    os.environ.pop("BUNNY_ROOM_STORE_URL", None)
    get_settings.cache_clear()
    get_room_store.cache_clear()
    get_live_room_manager.cache_clear()
    return TestClient(create_app())


def build_test_wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x01" * 16000)
    return buffer.getvalue()


def test_upload_turn_creates_room_history_and_returns_translation() -> None:
    client = make_mock_client()

    created_room = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    ).json()
    room_id = created_room["room_id"]
    participant_id = created_room["participants"][0]["participant_id"]

    response = client.post(
        f"/api/rooms/{room_id}/turns/upload",
        data={"participant_id": participant_id, "language": "ko"},
        files={"audio_file": ("turn.wav", build_test_wav_bytes(), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["delivery"] == "upload"
    assert body["speaker"]["participant_id"] == participant_id
    assert body["translations"]["es"].startswith("[ko->es]")

    turns_response = client.get(f"/api/rooms/{room_id}/turns")
    turns = turns_response.json()
    assert len(turns) == 1
    assert turns[0]["turn_id"] == body["turn_id"]


def test_upload_turn_broadcasts_final_and_translation_to_room_socket() -> None:
    client = make_mock_client()

    created_room = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    ).json()
    room_id = created_room["room_id"]
    participant_id = created_room["participants"][0]["participant_id"]

    with client.websocket_connect(f"/ws/rooms/{room_id}?participant_id={participant_id}") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "room_ready"

        response = client.post(
            f"/api/rooms/{room_id}/turns/upload",
            data={"participant_id": participant_id, "language": "ko"},
            files={"audio_file": ("turn.wav", build_test_wav_bytes(), "audio/wav")},
        )
        assert response.status_code == 200

        final_event = websocket.receive_json()
        translation_event = websocket.receive_json()

        assert final_event["type"] == "final"
        assert translation_event["type"] == "translation"
        assert translation_event["payload"]["speaker"]["participant_id"] == participant_id


def test_demo_turn_creates_history_and_broadcasts_translation() -> None:
    client = make_mock_client()

    created_room = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    ).json()
    room_id = created_room["room_id"]
    participant_id = created_room["participants"][0]["participant_id"]

    with client.websocket_connect(f"/ws/rooms/{room_id}?participant_id={participant_id}") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "room_ready"

        response = client.post(
            f"/api/rooms/{room_id}/turns/demo",
            json={
                "participant_id": participant_id,
                "language": "ko",
                "source_text": "안녕하세요, 데모 회의 시작할까요?",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["delivery"] == "demo"
        assert body["translations"]["es"].startswith("[ko->es]")

        final_event = websocket.receive_json()
        translation_event = websocket.receive_json()

        assert final_event["type"] == "final"
        assert final_event["payload"]["metrics"]["delivery"] == "demo"
        assert translation_event["type"] == "translation"
        assert translation_event["payload"]["turn_id"] == body["turn_id"]
        assert translation_event["payload"]["metrics"]["delivery"] == "demo"

        turns_response = client.get(f"/api/rooms/{room_id}/turns")
        turns = turns_response.json()
        assert len(turns) == 1
        assert turns[0]["delivery"] == "demo"


def test_demo_emoji_turn_skips_translation_but_still_broadcasts_final_turn() -> None:
    client = make_mock_client()

    created_room = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    ).json()
    room_id = created_room["room_id"]
    participant_id = created_room["participants"][0]["participant_id"]

    with client.websocket_connect(f"/ws/rooms/{room_id}?participant_id={participant_id}") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "room_ready"

        response = client.post(
            f"/api/rooms/{room_id}/turns/demo",
            json={
                "participant_id": participant_id,
                "language": "ko",
                "source_text": "🍺",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["source_text"] == "🍺"
        assert body["translations"] == {}

        final_event = websocket.receive_json()
        translation_event = websocket.receive_json()

        assert final_event["type"] == "final"
        assert final_event["payload"]["text"] == "🍺"
        assert translation_event["type"] == "translation"
        assert translation_event["payload"]["is_final"] is True
        assert translation_event["payload"]["translations"] == {}
