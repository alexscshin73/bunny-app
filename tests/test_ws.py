import os

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def make_mock_client() -> TestClient:
    os.environ["BUNNY_ASR_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_TARGETS"] = "[\"ko\",\"es\"]"
    os.environ["BUNNY_VAD_ENABLED"] = "false"
    get_settings.cache_clear()
    app = create_app()
    return TestClient(app)


def test_websocket_stream_emits_ready_partial_translation_and_final() -> None:
    client = make_mock_client()

    with client.websocket_connect("/ws/audio") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "ready"
        assert ready["payload"]["targets"] == ["ko", "es"]
        assert ready["payload"]["asr"]["engine"] == "mock"
        assert ready["payload"]["asr"]["ready"] is True
        assert ready["payload"]["translation"]["engine"] == "mock"
        assert ready["payload"]["translation"]["ready"] is True

        websocket.send_json({"type": "start", "sample_rate": 16000, "language": "auto"})
        started = websocket.receive_json()
        assert started["type"] == "session_started"

        websocket.send_bytes(b"\x00\x01" * 40000)
        partial = websocket.receive_json()
        translation = websocket.receive_json()

        assert partial["type"] == "partial"
        assert translation["type"] == "translation"

        websocket.send_json({"type": "stop"})
        final_event = websocket.receive_json()
        final_translation = websocket.receive_json()
        stats = websocket.receive_json()

        assert final_event["type"] == "final"
        assert final_event["payload"]["text"] == partial["payload"]["text"]
        assert final_translation["type"] == "translation"
        assert final_translation["payload"]["is_final"] is True
        assert stats["type"] == "stats"
        assert stats["payload"]["buffered_audio_bytes"] == 0


def test_healthz_exposes_runtime_status() -> None:
    client = make_mock_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["asr"]["engine"] == "mock"
    assert body["translation"]["engine"] == "mock"
    assert body["translation"]["targets"] == ["ko", "es"]
    llm_postedit = body.get("llm_postedit", {})
    assert llm_postedit.get("enabled") is False
    if "scope" in llm_postedit:
        assert llm_postedit["scope"] == "final"
    room_store = body.get("room_store")
    if room_store is not None:
        assert room_store.get("backend") in {"memory", "sqlite", "postgres"}
        assert room_store.get("max_participants") == 5
    speech_runtime = body.get("speech_runtime")
    if speech_runtime is not None:
        assert speech_runtime.get("vad_enabled") is False
        assert speech_runtime.get("segment_emit_ms") == 800


def test_brand_image_is_served() -> None:
    client = make_mock_client()

    response = client.get("/bunny-ai.png")

    assert response.status_code == 200
