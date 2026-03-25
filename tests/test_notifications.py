import os
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.config import get_settings
from app.deps.auth import _get_cached_user_store
from app.main import create_app
from app.services.live_rooms import get_live_room_manager
from app.services.rooms import get_room_store


def configure_sqlite_app(db_path: str) -> None:
    os.environ["BUNNY_ROOM_STORE_BACKEND"] = "sqlite"
    os.environ["BUNNY_ROOM_STORE_PATH"] = db_path
    os.environ["BUNNY_ROOM_MAX_PARTICIPANTS"] = "5"
    os.environ["BUNNY_ASR_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_ENGINE"] = "mock"
    os.environ["BUNNY_TRANSLATION_TARGETS"] = "[\"ko\",\"es\"]"
    os.environ["BUNNY_VAD_ENABLED"] = "false"
    os.environ["BUNNY_WEB_PUSH_PUBLIC_KEY"] = "BEl6dummyPublicKey1234567890abcdefghijklmno"
    os.environ["BUNNY_WEB_PUSH_PRIVATE_KEY"] = "dummy-private-key"
    os.environ["BUNNY_WEB_PUSH_SUBJECT"] = "mailto:alerts@bunny.test"
    get_settings.cache_clear()
    get_room_store.cache_clear()
    get_live_room_manager.cache_clear()
    _get_cached_user_store.cache_clear()


def register_user(client: TestClient, display_name: str, phone: str, language: str) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "display_name": display_name,
            "phone": phone,
            "icon": "",
            "bio": "",
            "preferred_language": language,
            "password": "pass1234",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["user"]


def test_joining_invite_creates_invite_notification() -> None:
    with TemporaryDirectory() as tmp_dir:
        configure_sqlite_app(f"{tmp_dir}/rooms.sqlite3")
        app = create_app()
        host_client = TestClient(app)
        guest_client = TestClient(app)

        register_user(host_client, "Minji", "+821012341234", "ko")
        register_user(guest_client, "Luis", "+5215512345678", "es")

        room_response = host_client.post(
            "/api/rooms",
            json={"display_name": "Minji", "title": "Border Chat", "language": "ko"},
        )
        assert room_response.status_code == 201, room_response.text
        room = room_response.json()

        join_response = guest_client.post(
            f"/api/rooms/invites/{room['invite_code']}/join",
            json={"display_name": "Luis", "language": "es"},
        )
        assert join_response.status_code == 200, join_response.text

        notifications_response = guest_client.get("/api/me/notifications")
        assert notifications_response.status_code == 200, notifications_response.text
        notifications = notifications_response.json()

        assert len(notifications) == 1
        assert notifications[0]["notification_type"] == "invite"
        assert notifications[0]["room_id"] == room["room_id"]
        assert notifications[0]["room_title"] == "Border Chat"
        assert "Minji invited you" in notifications[0]["body"]


def test_new_turn_creates_notification_for_other_member_and_can_be_read() -> None:
    with TemporaryDirectory() as tmp_dir:
        configure_sqlite_app(f"{tmp_dir}/rooms.sqlite3")
        app = create_app()
        host_client = TestClient(app)
        guest_client = TestClient(app)

        register_user(host_client, "Minji", "+821012341234", "ko")
        register_user(guest_client, "Luis", "+5215512345678", "es")

        room_response = host_client.post(
            "/api/rooms",
            json={"display_name": "Minji", "title": "Border Chat", "language": "ko"},
        )
        room = room_response.json()
        host_participant_id = room["participants"][0]["participant_id"]

        join_response = guest_client.post(
            f"/api/rooms/invites/{room['invite_code']}/join",
            json={"display_name": "Luis", "language": "es"},
        )
        assert join_response.status_code == 200, join_response.text

        turn_response = host_client.post(
            f"/api/rooms/{room['room_id']}/turns/demo",
            json={
                "participant_id": host_participant_id,
                "language": "ko",
                "source_text": "안녕하세요, 메시지 알림 테스트입니다.",
            },
        )
        assert turn_response.status_code == 200, turn_response.text

        notifications_response = guest_client.get("/api/me/notifications")
        notifications = notifications_response.json()

        turn_notification = next(
            item for item in notifications if item["notification_type"] == "turn"
        )
        assert turn_notification["room_id"] == room["room_id"]
        assert turn_notification["actor_name"] == "Minji"
        assert turn_notification["read_at"] is None

        read_response = guest_client.post(
            f"/api/me/notifications/{turn_notification['notification_id']}/read"
        )
        assert read_response.status_code == 200, read_response.text

        refreshed_notifications = guest_client.get("/api/me/notifications").json()
        refreshed_turn_notification = next(
            item
            for item in refreshed_notifications
            if item["notification_id"] == turn_notification["notification_id"]
        )
        assert refreshed_turn_notification["read_at"] is not None


def test_manual_announcement_notification_can_be_created() -> None:
    with TemporaryDirectory() as tmp_dir:
        configure_sqlite_app(f"{tmp_dir}/rooms.sqlite3")
        app = create_app()
        client = TestClient(app)

        register_user(client, "Minji", "+821012341234", "ko")

        create_response = client.post(
            "/api/me/notifications/announcements",
            json={
                "title": "Service notice",
                "body": "Realtime translation maintenance starts at 22:00.",
            },
        )
        assert create_response.status_code == 201, create_response.text
        body = create_response.json()
        assert body["notification_type"] == "announcement"
        assert body["title"] == "Service notice"

        notifications = client.get("/api/me/notifications").json()
        assert notifications[0]["notification_type"] == "announcement"


def test_web_push_subscription_can_be_saved_and_removed() -> None:
    with TemporaryDirectory() as tmp_dir:
        configure_sqlite_app(f"{tmp_dir}/rooms.sqlite3")
        app = create_app()
        client = TestClient(app)

        register_user(client, "Minji", "+821012341234", "ko")

        config_response = client.get("/api/me/web-push/config")
        assert config_response.status_code == 200, config_response.text
        assert config_response.json()["configured"] is True

        subscription = {
            "endpoint": "https://push.example.test/subscriptions/abc",
            "expirationTime": None,
            "keys": {
                "auth": "test-auth",
                "p256dh": "test-p256dh",
            },
        }

        save_response = client.post(
            "/api/me/web-push/subscriptions",
            json={"subscription": subscription},
        )
        assert save_response.status_code == 204, save_response.text

        delete_response = client.request(
            "DELETE",
            "/api/me/web-push/subscriptions",
            json={"endpoint": subscription["endpoint"]},
        )
        assert delete_response.status_code == 204, delete_response.text
