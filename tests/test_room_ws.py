import os

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


def test_room_websocket_broadcasts_speaker_events_to_other_participants() -> None:
    client = make_mock_client()

    created_room = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    ).json()
    room_id = created_room["room_id"]
    host_id = created_room["participants"][0]["participant_id"]

    joined_room = client.post(
        f"/api/rooms/{room_id}/join",
        json={"display_name": "Luis", "language": "es"},
    ).json()
    guest = next(
        participant for participant in joined_room["participants"] if participant["participant_id"] != host_id
    )

    with client.websocket_connect(f"/ws/rooms/{room_id}?participant_id={host_id}") as host_ws:
        host_ready = host_ws.receive_json()
        assert host_ready["type"] == "room_ready"
        assert host_ready["payload"]["participant"]["participant_id"] == host_id

        with client.websocket_connect(
            f"/ws/rooms/{room_id}?participant_id={guest['participant_id']}"
        ) as guest_ws:
            guest_ready = guest_ws.receive_json()
            host_joined = host_ws.receive_json()

            assert guest_ready["type"] == "room_ready"
            assert host_joined["type"] == "participant_joined"
            assert host_joined["payload"]["participant"]["participant_id"] == guest["participant_id"]

            host_ws.send_json({"type": "start", "sample_rate": 16000, "language": "ko"})
            started = host_ws.receive_json()
            host_speaker_started = host_ws.receive_json()
            guest_speaker_started = guest_ws.receive_json()
            assert started["type"] == "session_started"
            assert started["payload"]["speaker"]["participant_id"] == host_id
            assert host_speaker_started["type"] == "speaker_state"
            assert host_speaker_started["payload"]["active"] is True
            assert guest_speaker_started["type"] == "speaker_state"
            assert guest_speaker_started["payload"]["speaker"]["participant_id"] == host_id
            assert guest_speaker_started["payload"]["active"] is True

            host_ws.send_bytes(b"\x00\x01" * 40000)

            host_partial = host_ws.receive_json()
            host_translation = host_ws.receive_json()
            guest_partial = guest_ws.receive_json()
            guest_translation = guest_ws.receive_json()

            assert host_partial["type"] == "partial"
            assert guest_partial["type"] == "partial"
            assert host_translation["type"] == "translation"
            assert guest_translation["type"] == "translation"
            assert host_translation["payload"]["speaker"]["participant_id"] == host_id
            assert guest_translation["payload"]["speaker"]["participant_id"] == host_id
            assert guest_translation["payload"]["translations"]["es"].startswith("[ko->es]")
            assert "turn_id" not in guest_translation["payload"]

            host_ws.send_json({"type": "stop"})
            _host_final = host_ws.receive_json()
            host_final_translation = host_ws.receive_json()
            _host_stats = host_ws.receive_json()
            host_speaker_stopped = host_ws.receive_json()
            _guest_final = guest_ws.receive_json()
            guest_final_translation = guest_ws.receive_json()
            guest_speaker_stopped = guest_ws.receive_json()

            assert host_final_translation["type"] == "translation"
            assert guest_final_translation["type"] == "translation"
            assert guest_final_translation["payload"]["turn_id"]
            assert host_speaker_stopped["type"] == "speaker_state"
            assert host_speaker_stopped["payload"]["active"] is False
            assert guest_speaker_stopped["type"] == "speaker_state"
            assert guest_speaker_stopped["payload"]["active"] is False

            turns_response = client.get(f"/api/rooms/{room_id}/turns")
            assert turns_response.status_code == 200
            turns = turns_response.json()
            assert len(turns) == 1
            assert turns[0]["delivery"] == "realtime"
            assert turns[0]["turn_id"] == guest_final_translation["payload"]["turn_id"]
