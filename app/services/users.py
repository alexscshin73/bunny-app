from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3

from app.models.users import (
    UserNotification,
    UserProfile,
    WebPushSubscription,
    UserRoomParticipantVisual,
    UserRoomSummary,
)


SESSION_COOKIE_NAME = "bunny_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30


class UserAlreadyExistsError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class UserNotFoundError(KeyError):
    pass


class RoomHistoryNotFoundError(KeyError):
    pass


class SQLiteUserStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    icon TEXT NOT NULL DEFAULT '',
                    bio TEXT NOT NULL DEFAULT '',
                    notifications_enabled INTEGER NOT NULL DEFAULT 1,
                    password_salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT
                );

                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS user_room_memberships (
                    user_id TEXT NOT NULL,
                    room_id TEXT NOT NULL,
                    participant_id TEXT NOT NULL,
                    joined_at TEXT NOT NULL,
                    PRIMARY KEY(user_id, room_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_room_memberships_user_id
                ON user_room_memberships(user_id, joined_at DESC);

                CREATE TABLE IF NOT EXISTS user_notifications (
                    notification_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    room_id TEXT,
                    room_title TEXT NOT NULL DEFAULT '',
                    actor_user_id TEXT,
                    actor_name TEXT NOT NULL DEFAULT '',
                    actor_icon TEXT NOT NULL DEFAULT '',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    read_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id_created_at
                ON user_notifications(user_id, created_at DESC);

                CREATE TABLE IF NOT EXISTS user_push_subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL UNIQUE,
                    subscription_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_user_push_subscriptions_user_id
                ON user_push_subscriptions(user_id, last_seen_at DESC);
                """
            )
            user_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            if "preferred_language" not in user_columns:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN preferred_language TEXT"
                )
            if "bio" not in user_columns:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN bio TEXT NOT NULL DEFAULT ''"
                )
            if "notifications_enabled" not in user_columns:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN notifications_enabled INTEGER NOT NULL DEFAULT 1"
                )
            notification_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(user_notifications)").fetchall()
            }
            if notification_columns and "room_title" not in notification_columns:
                connection.execute(
                    "ALTER TABLE user_notifications ADD COLUMN room_title TEXT NOT NULL DEFAULT ''"
                )
            if notification_columns and "actor_user_id" not in notification_columns:
                connection.execute(
                    "ALTER TABLE user_notifications ADD COLUMN actor_user_id TEXT"
                )
            if notification_columns and "metadata_json" not in notification_columns:
                connection.execute(
                    "ALTER TABLE user_notifications ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}'"
                )
            push_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(user_push_subscriptions)").fetchall()
            }
            if push_columns and "last_seen_at" not in push_columns:
                connection.execute(
                    "ALTER TABLE user_push_subscriptions ADD COLUMN last_seen_at TEXT NOT NULL DEFAULT ''"
                )
                connection.execute(
                    """
                    UPDATE user_push_subscriptions
                    SET last_seen_at = CASE
                        WHEN last_seen_at = '' THEN created_at
                        ELSE last_seen_at
                    END
                    """
                )

    def register_user(
        self,
        display_name: str,
        phone: str,
        icon: str,
        bio: str,
        preferred_language: str | None,
        notifications_enabled: bool,
        password: str,
    ) -> UserProfile:
        normalized_phone = normalize_phone(phone)
        created_at = datetime.now(UTC)
        user_id = secrets.token_hex(8)
        password_salt = secrets.token_hex(16)
        password_hash = hash_password(password, password_salt)
        resolved_icon = (icon or "").strip()

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT user_id FROM users WHERE phone = ?",
                (normalized_phone,),
            ).fetchone()
            if existing is not None:
                raise UserAlreadyExistsError(normalized_phone)
            connection.execute(
                """
                INSERT INTO users (
                    user_id, display_name, phone, icon, password_salt, password_hash,
                    bio, preferred_language, notifications_enabled, created_at, last_login_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    display_name.strip(),
                    normalized_phone,
                    resolved_icon,
                    password_salt,
                    password_hash,
                    (bio or "").strip(),
                    normalize_preferred_language(preferred_language),
                    1 if notifications_enabled else 0,
                    created_at.isoformat(),
                    created_at.isoformat(),
                ),
            )
        return self.get_user(user_id)

    def authenticate(self, phone: str, password: str) -> UserProfile:
        normalized_phone = normalize_phone(phone)
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    user_id, display_name, phone, icon, bio, preferred_language, notifications_enabled, password_salt, password_hash,
                    created_at, last_login_at
                FROM users
                WHERE phone = ?
                """,
                (normalized_phone,),
            ).fetchone()
            if row is None:
                raise InvalidCredentialsError(normalized_phone)

            candidate_hash = hash_password(password, row["password_salt"])
            if candidate_hash != row["password_hash"]:
                raise InvalidCredentialsError(normalized_phone)

            logged_in_at = datetime.now(UTC)
            connection.execute(
                "UPDATE users SET last_login_at = ? WHERE user_id = ?",
                (logged_in_at.isoformat(), row["user_id"]),
            )
        return self.get_user(row["user_id"])

    def create_session(self, user_id: str) -> str:
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(seconds=SESSION_MAX_AGE_SECONDS)
        session_token = secrets.token_urlsafe(32)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_sessions (session_token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_token,
                    user_id,
                    created_at.isoformat(),
                    expires_at.isoformat(),
                ),
            )
        return session_token

    def delete_session(self, session_token: str) -> None:
        if not session_token:
            return
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM user_sessions WHERE session_token = ?",
                (session_token,),
            )

    def get_user_by_session(self, session_token: str | None) -> UserProfile | None:
        if not session_token:
            return None
        self.cleanup_expired_sessions()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    users.user_id,
                    users.display_name,
                    users.phone,
                    users.icon,
                    users.bio,
                    users.preferred_language,
                    users.notifications_enabled,
                    users.created_at,
                    users.last_login_at
                FROM user_sessions
                JOIN users ON users.user_id = user_sessions.user_id
                WHERE user_sessions.session_token = ?
                """,
                (session_token,),
            ).fetchone()
        if row is None:
            return None
        return user_profile_from_row(row)

    def get_user(self, user_id: str) -> UserProfile:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT user_id, display_name, phone, icon, bio, preferred_language, notifications_enabled, created_at, last_login_at
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            raise UserNotFoundError(user_id)
        return user_profile_from_row(row)

    def update_user(
        self,
        user_id: str,
        display_name: str,
        icon: str,
        bio: str,
        preferred_language: str | None,
        notifications_enabled: bool,
    ) -> UserProfile:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE users
                SET display_name = ?, icon = ?, bio = ?, preferred_language = ?, notifications_enabled = ?
                WHERE user_id = ?
                """,
                (
                    display_name.strip(),
                    (icon or "").strip(),
                    (bio or "").strip(),
                    normalize_preferred_language(preferred_language),
                    1 if notifications_enabled else 0,
                    user_id,
                ),
            )
        if not cursor.rowcount:
            raise UserNotFoundError(user_id)
        return self.get_user(user_id)

    def user_notifications_enabled(self, user_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT notifications_enabled
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            raise UserNotFoundError(user_id)
        return bool(row["notifications_enabled"])

    def cleanup_expired_sessions(self) -> int:
        cutoff = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM user_sessions WHERE expires_at < ?",
                (cutoff,),
            )
        return cursor.rowcount if cursor.rowcount != -1 else 0

    def record_room_membership(self, user_id: str, room_id: str, participant_id: str) -> None:
        joined_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_room_memberships (user_id, room_id, participant_id, joined_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, room_id) DO UPDATE SET
                    participant_id = excluded.participant_id,
                    joined_at = excluded.joined_at
                """,
                (user_id, room_id, participant_id, joined_at),
            )

    def list_room_history(self, user_id: str) -> list[UserRoomSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    memberships.room_id,
                    memberships.participant_id,
                    rooms.title AS room_title,
                    memberships.joined_at,
                    rooms.status,
                    rooms.created_at,
                    rooms.last_activity_at,
                    COALESCE(
                        (
                            SELECT other_participants.display_name
                            FROM participants AS other_participants
                            WHERE other_participants.room_id = memberships.room_id
                              AND other_participants.participant_id != memberships.participant_id
                            ORDER BY other_participants.joined_at DESC
                            LIMIT 1
                        ),
                        'Waiting for participant'
                    ) AS counterpart_name,
                    COALESCE(
                        (
                            SELECT other_participants.icon
                            FROM participants AS other_participants
                            WHERE other_participants.room_id = memberships.room_id
                              AND other_participants.participant_id != memberships.participant_id
                            ORDER BY other_participants.joined_at DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS counterpart_icon,
                    COALESCE(
                        (
                            SELECT
                                CASE
                                    WHEN latest_turn.turn_type = 'attachment' THEN COALESCE(NULLIF(latest_turn.attachment_name, ''), 'Sent an attachment.')
                                    WHEN latest_turn.source_text != '' THEN latest_turn.source_text
                                    ELSE 'No saved conversation yet.'
                                END
                            FROM turns AS latest_turn
                            WHERE latest_turn.room_id = memberships.room_id
                            ORDER BY latest_turn.created_at DESC
                            LIMIT 1
                        ),
                        'No conversation yet.'
                    ) AS last_message,
                    COUNT(DISTINCT participants.participant_id) AS participant_count,
                    COUNT(DISTINCT turns.turn_id) AS turn_count
                FROM user_room_memberships AS memberships
                JOIN rooms ON rooms.room_id = memberships.room_id
                LEFT JOIN participants ON participants.room_id = memberships.room_id
                LEFT JOIN turns ON turns.room_id = memberships.room_id
                WHERE memberships.user_id = ?
                GROUP BY
                    memberships.room_id,
                    memberships.joined_at,
                    rooms.status,
                    rooms.created_at,
                    rooms.last_activity_at
                ORDER BY rooms.last_activity_at DESC
                """,
                (user_id,),
            ).fetchall()
            summaries = []
            for row in rows:
                participant_visual_rows = connection.execute(
                    """
                    SELECT display_name, icon
                    FROM participants
                    WHERE room_id = ?
                    ORDER BY joined_at ASC
                    LIMIT 4
                    """,
                    (row["room_id"],),
                ).fetchall()
                summaries.append(
                    UserRoomSummary(
                        room_id=row["room_id"],
                        participant_id=row["participant_id"],
                        room_title=row["room_title"] or "",
                        status=row["status"],
                        participant_count=row["participant_count"],
                        turn_count=row["turn_count"],
                        counterpart_name=row["counterpart_name"],
                        counterpart_icon=row["counterpart_icon"] or "",
                        participant_visuals=[
                            UserRoomParticipantVisual(
                                display_name=visual_row["display_name"],
                                icon=visual_row["icon"] or "",
                            )
                            for visual_row in participant_visual_rows
                        ],
                        last_message=row["last_message"],
                        joined_at=parse_datetime(row["joined_at"]),
                        created_at=parse_datetime(row["created_at"]),
                        last_activity_at=parse_datetime(row["last_activity_at"]),
                    )
                )
        return summaries

    def get_room_membership(self, user_id: str, room_id: str) -> tuple[str, datetime]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT participant_id, joined_at
                FROM user_room_memberships
                WHERE user_id = ? AND room_id = ?
                """,
                (user_id, room_id),
            ).fetchone()
        if row is None:
            raise RoomHistoryNotFoundError(room_id)
        return row["participant_id"], parse_datetime(row["joined_at"])

    def delete_room_history(self, user_id: str, room_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM user_room_memberships
                WHERE user_id = ? AND room_id = ?
                """,
                (user_id, room_id),
            )
        return bool(cursor.rowcount)

    def list_room_member_user_ids(self, room_id: str, exclude_user_id: str | None = None) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT user_id
                FROM user_room_memberships
                WHERE room_id = ?
                  AND user_id IS NOT NULL
                """,
                (room_id,),
            ).fetchall()
        user_ids = [row["user_id"] for row in rows if row["user_id"]]
        if exclude_user_id:
            user_ids = [user_id for user_id in user_ids if user_id != exclude_user_id]
        return user_ids

    def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
        *,
        room_id: str | None = None,
        room_title: str = "",
        actor_user_id: str | None = None,
        actor_name: str = "",
        actor_icon: str = "",
        metadata: dict[str, object] | None = None,
    ) -> UserNotification:
        notification = UserNotification(
            notification_id=secrets.token_hex(12),
            user_id=user_id,
            notification_type=notification_type,
            title=title.strip(),
            body=body.strip(),
            room_id=(room_id or "").strip() or None,
            room_title=(room_title or "").strip(),
            actor_user_id=(actor_user_id or "").strip() or None,
            actor_name=(actor_name or "").strip(),
            actor_icon=(actor_icon or "").strip(),
            metadata=dict(metadata or {}),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_notifications (
                    notification_id, user_id, notification_type, title, body,
                    room_id, room_title, actor_user_id, actor_name, actor_icon,
                    metadata_json, created_at, read_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification.notification_id,
                    notification.user_id,
                    notification.notification_type,
                    notification.title,
                    notification.body,
                    notification.room_id,
                    notification.room_title,
                    notification.actor_user_id,
                    notification.actor_name,
                    notification.actor_icon,
                    json.dumps(notification.metadata, ensure_ascii=False),
                    notification.created_at.isoformat(),
                    notification.read_at.isoformat() if notification.read_at else None,
                ),
            )
        return notification

    def list_notifications(self, user_id: str, limit: int = 50) -> list[UserNotification]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    notification_id,
                    user_id,
                    notification_type,
                    title,
                    body,
                    room_id,
                    room_title,
                    actor_user_id,
                    actor_name,
                    actor_icon,
                    metadata_json,
                    created_at,
                    read_at
                FROM user_notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, max(limit, 1)),
            ).fetchall()
        return [notification_from_row(row) for row in rows]

    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE user_notifications
                SET read_at = COALESCE(read_at, ?)
                WHERE user_id = ? AND notification_id = ?
                """,
                (datetime.now(UTC).isoformat(), user_id, notification_id),
            )
        return bool(cursor.rowcount)

    def mark_all_notifications_read(self, user_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE user_notifications
                SET read_at = COALESCE(read_at, ?)
                WHERE user_id = ?
                  AND read_at IS NULL
                """,
                (datetime.now(UTC).isoformat(), user_id),
            )
        return cursor.rowcount if cursor.rowcount != -1 else 0

    def save_push_subscription(self, user_id: str, subscription: WebPushSubscription) -> None:
        now = datetime.now(UTC).isoformat()
        subscription_json = subscription.model_dump_json()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_push_subscriptions (
                    subscription_id, user_id, endpoint, subscription_json, created_at, last_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(endpoint) DO UPDATE SET
                    user_id = excluded.user_id,
                    subscription_json = excluded.subscription_json,
                    last_seen_at = excluded.last_seen_at
                """,
                (
                    secrets.token_hex(12),
                    user_id,
                    subscription.endpoint,
                    subscription_json,
                    now,
                    now,
                ),
            )

    def list_push_subscriptions(self, user_id: str) -> list[WebPushSubscription]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT subscription_json
                FROM user_push_subscriptions
                WHERE user_id = ?
                ORDER BY last_seen_at DESC
                """,
                (user_id,),
            ).fetchall()
        subscriptions: list[WebPushSubscription] = []
        for row in rows:
            try:
                subscriptions.append(WebPushSubscription.model_validate_json(row["subscription_json"]))
            except ValueError:
                continue
        return subscriptions

    def delete_push_subscription(self, user_id: str, endpoint: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM user_push_subscriptions
                WHERE user_id = ? AND endpoint = ?
                """,
                (user_id, endpoint),
            )
        return bool(cursor.rowcount)

    @contextmanager
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def normalize_phone(phone: str) -> str:
    trimmed = phone.strip()
    if not trimmed:
        raise ValueError("Phone number is required.")
    normalized = re.sub(r"[^\d+]", "", trimmed)
    if normalized.count("+") > 1:
        raise ValueError("Phone number format is invalid.")
    if "+" in normalized and not normalized.startswith("+"):
        raise ValueError("Phone number format is invalid.")
    digits_only = normalized[1:] if normalized.startswith("+") else normalized
    if len(digits_only) < 7:
        raise ValueError("Phone number must be at least 7 digits.")
    return normalized


def hash_password(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        200_000,
    ).hex()


def parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def normalize_preferred_language(value: str | None) -> str | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    if normalized not in {"ko", "es"}:
        raise ValueError("Preferred language must be ko or es.")
    return normalized


def user_profile_from_row(row: sqlite3.Row) -> UserProfile:
    return UserProfile(
        user_id=row["user_id"],
        display_name=row["display_name"],
        phone=row["phone"],
        icon=row["icon"],
        bio=row["bio"] or "",
        preferred_language=normalize_preferred_language(row["preferred_language"]),
        notifications_enabled=bool(row["notifications_enabled"]) if "notifications_enabled" in row.keys() else True,
        created_at=parse_datetime(row["created_at"]) or datetime.now(UTC),
        last_login_at=parse_datetime(row["last_login_at"]),
    )


def notification_from_row(row: sqlite3.Row) -> UserNotification:
    metadata_raw = row["metadata_json"] or "{}"
    try:
        metadata = json.loads(metadata_raw)
    except json.JSONDecodeError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return UserNotification(
        notification_id=row["notification_id"],
        user_id=row["user_id"],
        notification_type=row["notification_type"],
        title=row["title"],
        body=row["body"],
        room_id=row["room_id"] or None,
        room_title=row["room_title"] or "",
        actor_user_id=row["actor_user_id"] or None,
        actor_name=row["actor_name"] or "",
        actor_icon=row["actor_icon"] or "",
        metadata=metadata,
        created_at=parse_datetime(row["created_at"]) or datetime.now(UTC),
        read_at=parse_datetime(row["read_at"]),
    )
