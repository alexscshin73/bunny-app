import os
from tempfile import TemporaryDirectory
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.services.rooms import get_room_store


def make_client() -> TestClient:
    os.environ["BUNNY_ROOM_STORE_BACKEND"] = "memory"
    os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"
    os.environ.pop("BUNNY_ROOM_STORE_URL", None)
    get_settings.cache_clear()
    get_room_store.cache_clear()
    return TestClient(create_app())


def test_create_and_join_room() -> None:
    client = make_client()

    create_response = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko"},
    )
    assert create_response.status_code == 201

    room = create_response.json()
    assert room["status"] == "waiting"
    assert room["participant_count"] == 1
    assert room["participants"][0]["language"] == "ko"

    join_response = client.post(
        f"/api/rooms/{room['room_id']}/join",
        json={"display_name": "Luis", "language": "es"},
    )
    assert join_response.status_code == 200

    joined_room = join_response.json()
    assert joined_room["status"] == "ready"
    assert joined_room["participant_count"] == 2
    assert {participant["language"] for participant in joined_room["participants"]} == {"ko", "es"}


def test_join_rejects_duplicate_language() -> None:
    client = make_client()

    create_response = client.post(
        "/api/rooms",
        json={"display_name": "Host", "language": "ko"},
    )
    room_id = create_response.json()["room_id"]

    join_response = client.post(
        f"/api/rooms/{room_id}/join",
        json={"display_name": "Guest", "language": "ko"},
    )

    assert join_response.status_code == 409
    assert join_response.json()["detail"] == "Room already has a participant using that language"


def test_create_and_join_room_allow_auto_language_for_both_participants() -> None:
    client = make_client()

    create_response = client.post(
        "/api/rooms",
        json={"display_name": "Host", "language": "auto"},
    )
    assert create_response.status_code == 201
    room_id = create_response.json()["room_id"]

    join_response = client.post(
        f"/api/rooms/{room_id}/join",
        json={"display_name": "Guest", "language": "auto"},
    )

    assert join_response.status_code == 200
    joined_room = join_response.json()
    assert joined_room["participant_count"] == 2
    assert {participant["language"] for participant in joined_room["participants"]} == {"auto"}


def test_create_room_accepts_requested_room_id() -> None:
    client = make_client()

    create_response = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko", "room_id": "A1B2C3"},
    )

    assert create_response.status_code == 201
    assert create_response.json()["room_id"] == "A1B2C3"


def test_create_room_rejects_duplicate_requested_room_id() -> None:
    client = make_client()

    first_response = client.post(
        "/api/rooms",
        json={"display_name": "Minji", "language": "ko", "room_id": "1303-01"},
    )
    duplicate_response = client.post(
        "/api/rooms",
        json={"display_name": "Luis", "language": "es", "room_id": "1303-01"},
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Room ID already exists"


def test_sqlite_room_store_persists_data_across_app_instances() -> None:
    with TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/rooms.sqlite3"
        os.environ["BUNNY_ROOM_STORE_BACKEND"] = "sqlite"
        os.environ["BUNNY_ROOM_STORE_PATH"] = db_path
        os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"
        get_settings.cache_clear()
        get_room_store.cache_clear()

        first_client = TestClient(create_app())
        create_response = first_client.post(
            "/api/rooms",
            json={"display_name": "Minji", "language": "ko"},
        )
        room_id = create_response.json()["room_id"]
        first_client.post(
            f"/api/rooms/{room_id}/join",
            json={"display_name": "Luis", "language": "es"},
        )

        get_settings.cache_clear()
        get_room_store.cache_clear()
        second_client = TestClient(create_app())
        persisted_room = second_client.get(f"/api/rooms/{room_id}")

        assert persisted_room.status_code == 200
        body = persisted_room.json()
        assert body["participant_count"] == 2
        assert body["status"] == "ready"


def test_sqlite_room_store_prunes_expired_rooms() -> None:
    with TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/rooms.sqlite3"
        os.environ["BUNNY_ROOM_STORE_BACKEND"] = "sqlite"
        os.environ["BUNNY_ROOM_STORE_PATH"] = db_path
        os.environ["BUNNY_ROOM_TTL_MINUTES"] = "1"
        os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"
        get_settings.cache_clear()
        get_room_store.cache_clear()

        client = TestClient(create_app())
        create_response = client.post(
            "/api/rooms",
            json={"display_name": "Minji", "language": "ko"},
        )
        room_id = create_response.json()["room_id"]

        import sqlite3

        with sqlite3.connect(db_path) as connection:
            connection.execute(
                "UPDATE rooms SET last_activity_at = ? WHERE room_id = ?",
                ((datetime.now(UTC) - timedelta(minutes=10)).isoformat(), room_id),
            )

        get_settings.cache_clear()
        get_room_store.cache_clear()
        expired_client = TestClient(create_app())
        room_response = expired_client.get(f"/api/rooms/{room_id}")
        list_response = expired_client.get("/api/rooms")

        assert room_response.status_code == 404
        assert list_response.status_code == 200
        assert list_response.json() == []


def test_manual_cleanup_endpoint_removes_expired_rooms() -> None:
    with TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/rooms.sqlite3"
        os.environ["BUNNY_ROOM_STORE_BACKEND"] = "sqlite"
        os.environ["BUNNY_ROOM_STORE_PATH"] = db_path
        os.environ["BUNNY_ROOM_TTL_MINUTES"] = "1"
        os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "2"
        get_settings.cache_clear()
        get_room_store.cache_clear()

        client = TestClient(create_app())
        create_response = client.post(
            "/api/rooms",
            json={"display_name": "Minji", "language": "ko"},
        )
        room_id = create_response.json()["room_id"]

        import sqlite3

        with sqlite3.connect(db_path) as connection:
            connection.execute(
                "UPDATE rooms SET last_activity_at = ? WHERE room_id = ?",
                ((datetime.now(UTC) - timedelta(minutes=10)).isoformat(), room_id),
            )

        cleanup_response = client.post("/api/rooms/_cleanup")
        list_response = client.get("/api/rooms")

        assert cleanup_response.status_code == 200
        assert cleanup_response.json() == {"cleaned_rooms": 1}
        assert list_response.status_code == 200
        assert list_response.json() == []


def test_postgres_backend_requires_store_url() -> None:
    get_room_store.cache_clear()

    try:
        get_room_store(
            backend="postgres",
            db_path="unused.sqlite3",
            db_url=None,
            max_participants=2,
            ttl_minutes=1440,
        )
    except RuntimeError as exc:
        assert "BUNNY_ROOM_STORE_URL" in str(exc)
    else:
        raise AssertionError("expected postgres backend without URL to fail")


def test_unknown_room_store_backend_raises_error() -> None:
    get_room_store.cache_clear()

    try:
        get_room_store(
            backend="mystery",
            db_path="unused.sqlite3",
            db_url=None,
            max_participants=2,
            ttl_minutes=1440,
        )
    except ValueError as exc:
        assert "Unsupported room store backend" in str(exc)
    else:
        raise AssertionError("expected unknown backend to fail")
