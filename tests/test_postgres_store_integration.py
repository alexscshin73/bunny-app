import os
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.services.rooms import get_room_store


POSTGRES_URL = os.getenv("BUNNY_TEST_POSTGRES_URL")


@pytest.mark.skipif(
    not POSTGRES_URL,
    reason="Set BUNNY_TEST_POSTGRES_URL to run the Postgres integration smoke test.",
)
def test_postgres_room_store_smoke_flow() -> None:
    pytest.importorskip("psycopg")

    os.environ["BUNNY_ROOM_STORE_BACKEND"] = "postgres"
    os.environ["BUNNY_ROOM_STORE_URL"] = POSTGRES_URL or ""
    os.environ["BUNNY_ROOM_TTL_MINUTES"] = "1"
    os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"

    get_settings.cache_clear()
    get_room_store.cache_clear()

    client = TestClient(create_app())
    create_response = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    )
    assert create_response.status_code == 201
    room = create_response.json()
    room_id = room["room_id"]

    join_response = client.post(
        f"/api/rooms/{room_id}/join",
        json={"display_name": "Luis", "language": "es"},
    )
    assert join_response.status_code == 200
    assert join_response.json()["status"] == "ready"

    import psycopg

    with psycopg.connect(POSTGRES_URL) as connection:
        connection.execute(
            "UPDATE rooms SET last_activity_at = %s WHERE room_id = %s",
            (datetime.now(UTC) - timedelta(minutes=10), room_id),
        )

    cleanup_response = client.post("/api/rooms/_cleanup")
    assert cleanup_response.status_code == 200
    assert cleanup_response.json()["cleaned_rooms"] >= 1

    missing_room = client.get(f"/api/rooms/{room_id}")
    assert missing_room.status_code == 404
