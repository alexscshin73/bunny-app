from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from functools import lru_cache
import json
from pathlib import Path
import secrets
import sqlite3
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional backend
    psycopg = None
    dict_row = None

from app.models.rooms import (
    CreateRoomRequest,
    InviteRoomPreview,
    JoinRoomRequest,
    RoomAttachment,
    RoomDetail,
    RoomParticipant,
    RoomStatus,
    RoomSummary,
    RoomTurn,
    UpdateRoomRequest,
)

GUEST_NAME_PREFIX = "Guest"


class RoomNotFoundError(KeyError):
    pass


class RoomCapacityError(ValueError):
    pass


class RoomLanguageConflictError(ValueError):
    pass


class RoomAlreadyExistsError(ValueError):
    pass


def _guest_name_index(display_name: str) -> int | None:
    normalized = display_name.strip()
    if not normalized.startswith(GUEST_NAME_PREFIX):
        return None
    suffix = normalized[len(GUEST_NAME_PREFIX):].strip()
    if not suffix:
        return 1
    if suffix.isdigit():
        return max(int(suffix), 1)
    return None


def _next_guest_display_name(existing_names: list[str]) -> str:
    highest_index = 0
    for name in existing_names:
        guest_index = _guest_name_index(name)
        if guest_index is not None:
            highest_index = max(highest_index, guest_index)
    return f"{GUEST_NAME_PREFIX}{highest_index + 1}"


class RoomStore(ABC):
    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_rooms(self) -> list[RoomSummary]:
        raise NotImplementedError

    @abstractmethod
    def cleanup_expired_rooms(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def create_room(self, payload: CreateRoomRequest, user_id: str | None = None) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def update_room(self, room_id: str, payload: UpdateRoomRequest) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def get_room(self, room_id: str) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def get_room_by_invite_code(self, invite_code: str) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def get_participant(self, room_id: str, participant_id: str) -> RoomParticipant:
        raise NotImplementedError

    @abstractmethod
    def join_room(
        self,
        room_id: str,
        payload: JoinRoomRequest,
        participant_id: str | None = None,
        user_id: str | None = None,
    ) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def leave_room(self, room_id: str, participant_id: str) -> RoomDetail:
        raise NotImplementedError

    @abstractmethod
    def list_turns(self, room_id: str) -> list[RoomTurn]:
        raise NotImplementedError

    @abstractmethod
    def add_turn(
        self,
        room_id: str,
        participant: RoomParticipant,
        source_language: str,
        source_text: str,
        translations: dict[str, str],
        delivery: str,
        turn_type: str = "text",
        attachment: RoomAttachment | None = None,
    ) -> RoomTurn:
        raise NotImplementedError


@dataclass
class RoomRecord:
    room_id: str
    invite_code: str
    title: str
    created_at: datetime
    last_activity_at: datetime
    creator_participant_id: str | None = None
    participants: list[RoomParticipant] = field(default_factory=list)
    turns: list[RoomTurn] = field(default_factory=list)
    status: RoomStatus = "waiting"

    def to_summary(self) -> RoomSummary:
        return RoomSummary(
            room_id=self.room_id,
            invite_code=self.invite_code,
            title=self.title,
            status=self.status,
            participant_count=len(self.participants),
            creator_participant_id=self.creator_participant_id,
            created_at=self.created_at,
            last_activity_at=self.last_activity_at,
        )

    def to_detail(self) -> RoomDetail:
        return RoomDetail(
            room_id=self.room_id,
            invite_code=self.invite_code,
            title=self.title,
            status=self.status,
            participant_count=len(self.participants),
            creator_participant_id=self.creator_participant_id,
            created_at=self.created_at,
            last_activity_at=self.last_activity_at,
            participants=list(self.participants),
        )

    def to_invite_preview(self) -> InviteRoomPreview:
        return InviteRoomPreview(
            invite_code=self.invite_code,
            status=self.status,
            participant_count=len(self.participants),
            created_at=self.created_at,
            last_activity_at=self.last_activity_at,
            participants=list(self.participants),
        )


class InMemoryRoomStore(RoomStore):
    def __init__(self, max_participants: int = 2, ttl_minutes: int = 1440) -> None:
        self.max_participants = max(max_participants, 2)
        self.ttl_minutes = max(ttl_minutes, 1)
        self._rooms: dict[str, RoomRecord] = {}

    def initialize(self) -> None:
        return

    def list_rooms(self) -> list[RoomSummary]:
        self.cleanup_expired_rooms()
        return [room.to_summary() for room in self._rooms.values()]

    def cleanup_expired_rooms(self) -> int:
        return self._prune_expired_rooms()

    def create_room(self, payload: CreateRoomRequest, user_id: str | None = None) -> RoomDetail:
        room_id = self._generate_room_id()
        invite_code = self._generate_invite_code()
        participant = RoomParticipant(
            participant_id=self._generate_participant_id(),
            user_id=user_id,
            display_name=payload.display_name.strip(),
            icon=(payload.icon or "").strip(),
            language=payload.language,
        )
        room = RoomRecord(
            room_id=room_id,
            invite_code=invite_code,
            title=payload.title.strip(),
            created_at=datetime.now(UTC),
            last_activity_at=datetime.now(UTC),
            creator_participant_id=participant.participant_id,
            participants=[participant],
            status="waiting",
        )
        self._rooms[room_id] = room
        return room.to_detail()

    def update_room(self, room_id: str, payload: UpdateRoomRequest) -> RoomDetail:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        room.title = payload.title.strip()
        room.last_activity_at = datetime.now(UTC)
        return room.to_detail()

    def get_room(self, room_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        room.status = self._derive_status(len(room.participants))
        return room.to_detail()

    def get_room_by_invite_code(self, invite_code: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        room = next(
            (candidate for candidate in self._rooms.values() if candidate.invite_code == invite_code),
            None,
        )
        if room is None:
            raise RoomNotFoundError(invite_code)
        room.status = self._derive_status(len(room.participants))
        return room.to_detail()

    def get_participant(self, room_id: str, participant_id: str) -> RoomParticipant:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)

        for participant in room.participants:
            if participant.participant_id == participant_id:
                return participant

        raise RoomNotFoundError(participant_id)

    def join_room(
        self,
        room_id: str,
        payload: JoinRoomRequest,
        participant_id: str | None = None,
        user_id: str | None = None,
    ) -> RoomDetail:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        resolved_display_name = payload.display_name.strip()
        if user_id is None and not participant_id:
            resolved_display_name = _next_guest_display_name(
                [participant.display_name for participant in room.participants if participant.user_id is None]
            )

        if participant_id:
            for existing_participant in room.participants:
                if existing_participant.participant_id == participant_id:
                    existing_participant.user_id = user_id or existing_participant.user_id
                    existing_participant.display_name = resolved_display_name
                    existing_participant.icon = (payload.icon or "").strip()
                    existing_participant.language = payload.language
                    room.last_activity_at = datetime.now(UTC)
                    room.status = self._derive_status(len(room.participants))
                    return room.to_detail()
        if user_id:
            for existing_participant in room.participants:
                if existing_participant.user_id == user_id:
                    existing_participant.display_name = resolved_display_name
                    existing_participant.icon = (payload.icon or "").strip()
                    existing_participant.language = payload.language
                    room.last_activity_at = datetime.now(UTC)
                    room.status = self._derive_status(len(room.participants))
                    return room.to_detail()

        if len(room.participants) >= self.max_participants:
            raise RoomCapacityError(room_id)

        room.participants.append(
            RoomParticipant(
                participant_id=self._generate_participant_id(),
                user_id=user_id,
                display_name=resolved_display_name,
                icon=(payload.icon or "").strip(),
                language=payload.language,
            )
        )
        room.last_activity_at = datetime.now(UTC)
        room.status = self._derive_status(len(room.participants))
        return room.to_detail()

    def leave_room(self, room_id: str, participant_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        room.participants = [
            participant
            for participant in room.participants
            if participant.participant_id != participant_id
        ]
        room.last_activity_at = datetime.now(UTC)
        room.status = self._derive_status(len(room.participants))
        return room.to_detail()

    def list_turns(self, room_id: str) -> list[RoomTurn]:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        return list(room.turns)

    def add_turn(
        self,
        room_id: str,
        participant: RoomParticipant,
        source_language: str,
        source_text: str,
        translations: dict[str, str],
        delivery: str,
        turn_type: str = "text",
        attachment: RoomAttachment | None = None,
    ) -> RoomTurn:
        self.cleanup_expired_rooms()
        room = self._rooms.get(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)

        turn = RoomTurn(
            turn_id=self._generate_turn_id(),
            room_id=room_id,
            speaker=participant,
            source_language=source_language,
            source_text=source_text,
            translations=dict(translations),
            turn_type=turn_type,
            attachment=attachment,
            delivery=delivery,
        )
        room.turns.append(turn)
        room.last_activity_at = datetime.now(UTC)
        return turn

    def _derive_status(self, participant_count: int) -> RoomStatus:
        return "ready" if participant_count >= 2 else "waiting"

    def _generate_room_id(self) -> str:
        while True:
            room_id = f"room_{secrets.token_hex(8)}"
            if room_id not in self._rooms:
                return room_id

    def _generate_invite_code(self) -> str:
        existing_codes = {room.invite_code for room in self._rooms.values()}
        while True:
            invite_code = secrets.token_urlsafe(9)
            if invite_code not in existing_codes:
                return invite_code

    def _generate_participant_id(self) -> str:
        return secrets.token_hex(6)

    def _generate_turn_id(self) -> str:
        return secrets.token_hex(8)

    def _prune_expired_rooms(self) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=self.ttl_minutes)
        expired_room_ids = [
            room_id for room_id, room in self._rooms.items() if room.last_activity_at < cutoff
        ]
        for room_id in expired_room_ids:
            self._rooms.pop(room_id, None)
        return len(expired_room_ids)


class SQLiteRoomStore(RoomStore):
    def __init__(self, db_path: str, max_participants: int = 2, ttl_minutes: int = 1440) -> None:
        self.db_path = Path(db_path)
        self.max_participants = max(max_participants, 2)
        self.ttl_minutes = max(ttl_minutes, 1)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id TEXT PRIMARY KEY,
                    invite_code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    creator_participant_id TEXT,
                    created_at TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS participants (
                    participant_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    icon TEXT NOT NULL DEFAULT '',
                    language TEXT NOT NULL,
                    joined_at TEXT NOT NULL,
                    left_at TEXT,
                    FOREIGN KEY(room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    participant_id TEXT NOT NULL,
                    source_language TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translations_json TEXT NOT NULL,
                    turn_type TEXT NOT NULL DEFAULT 'text',
                    attachment_name TEXT NOT NULL DEFAULT '',
                    attachment_url TEXT NOT NULL DEFAULT '',
                    attachment_content_type TEXT NOT NULL DEFAULT '',
                    attachment_size_bytes INTEGER NOT NULL DEFAULT 0,
                    delivery TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
                    FOREIGN KEY(participant_id) REFERENCES participants(participant_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_participants_room_id ON participants(room_id);
                CREATE INDEX IF NOT EXISTS idx_turns_room_id ON turns(room_id, created_at);
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(rooms)").fetchall()
            }
            if "last_activity_at" not in columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN last_activity_at TEXT NOT NULL DEFAULT ''"
                )
                connection.execute(
                    """
                    UPDATE rooms
                    SET last_activity_at = CASE
                        WHEN last_activity_at = '' THEN created_at
                        ELSE last_activity_at
                    END
                    """
                )
            if "creator_participant_id" not in columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN creator_participant_id TEXT"
                )
            if "invite_code" not in columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN invite_code TEXT NOT NULL DEFAULT ''"
                )
                room_id_rows = connection.execute(
                    "SELECT room_id FROM rooms WHERE invite_code = ''"
                ).fetchall()
                for row in room_id_rows:
                    connection.execute(
                        "UPDATE rooms SET invite_code = ? WHERE room_id = ?",
                        (self._generate_invite_code(connection), row["room_id"]),
                    )
            if "title" not in columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN title TEXT NOT NULL DEFAULT ''"
                )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_rooms_invite_code ON rooms(invite_code)"
            )
            participant_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(participants)").fetchall()
            }
            if "icon" not in participant_columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN icon TEXT NOT NULL DEFAULT ''"
                )
            if "left_at" not in participant_columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN left_at TEXT"
                )
            if "user_id" not in participant_columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN user_id TEXT"
                )
            turn_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(turns)").fetchall()
            }
            if "turn_type" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN turn_type TEXT NOT NULL DEFAULT 'text'"
                )
            if "attachment_name" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_name TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_url" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_url TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_content_type" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_content_type TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_size_bytes" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_size_bytes INTEGER NOT NULL DEFAULT 0"
                )

    def list_rooms(self) -> list[RoomSummary]:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    rooms.room_id,
                    rooms.invite_code,
                    rooms.title,
                    rooms.status,
                    rooms.creator_participant_id,
                    rooms.created_at,
                    rooms.last_activity_at,
                    COUNT(participants.participant_id) AS participant_count
                FROM rooms
                LEFT JOIN participants
                    ON participants.room_id = rooms.room_id
                   AND participants.left_at IS NULL
                GROUP BY rooms.room_id
                ORDER BY rooms.created_at DESC
                """
            ).fetchall()
        return [
            RoomSummary(
                room_id=row["room_id"],
                invite_code=row["invite_code"],
                title=row["title"] or "",
                status=row["status"],
                participant_count=row["participant_count"],
                creator_participant_id=row["creator_participant_id"],
                created_at=_parse_datetime(row["created_at"]),
                last_activity_at=_parse_datetime(row["last_activity_at"]),
            )
            for row in rows
        ]

    def cleanup_expired_rooms(self) -> int:
        return self._prune_expired_rooms()

    def create_room(self, payload: CreateRoomRequest, user_id: str | None = None) -> RoomDetail:
        room_id = self._generate_room_id()
        invite_code = self._generate_invite_code()
        participant = RoomParticipant(
            participant_id=self._generate_participant_id(),
            user_id=user_id,
            display_name=payload.display_name.strip(),
            icon=(payload.icon or "").strip(),
            language=payload.language,
        )
        created_at = datetime.now(UTC)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO rooms (room_id, invite_code, title, status, creator_participant_id, created_at, last_activity_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    room_id,
                    invite_code,
                    payload.title.strip(),
                    "waiting",
                    participant.participant_id,
                    created_at.isoformat(),
                    created_at.isoformat(),
                ),
            )
            connection.execute(
                """
                INSERT INTO participants (participant_id, room_id, user_id, display_name, icon, language, joined_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    participant.participant_id,
                    room_id,
                    participant.user_id,
                    participant.display_name,
                    participant.icon,
                    participant.language,
                    participant.joined_at.isoformat(),
                ),
            )
        return self.get_room(room_id)

    def get_room(self, room_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                """
                SELECT room_id, invite_code, title, status, creator_participant_id, created_at, last_activity_at
                FROM rooms
                WHERE room_id = ?
                """,
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)

            participant_rows = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = ?
                  AND left_at IS NULL
                ORDER BY joined_at ASC
                """,
                (room_id,),
            ).fetchall()

            participant_count = len(participant_rows)
            derived_status = self._derive_status(participant_count)
            if room_row["status"] != derived_status:
                connection.execute(
                    "UPDATE rooms SET status = ? WHERE room_id = ?",
                    (derived_status, room_id),
                )

        participants = [_participant_from_row(row) for row in participant_rows]
        return RoomDetail(
            room_id=room_row["room_id"],
            invite_code=room_row["invite_code"],
            title=room_row["title"] or "",
            status=derived_status,
            participant_count=participant_count,
            creator_participant_id=room_row["creator_participant_id"],
            created_at=_parse_datetime(room_row["created_at"]),
            last_activity_at=_parse_datetime(room_row["last_activity_at"]),
            participants=participants,
        )

    def get_room_by_invite_code(self, invite_code: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                """
                SELECT room_id
                FROM rooms
                WHERE invite_code = ?
                """,
                (invite_code,),
            ).fetchone()
        if room_row is None:
            raise RoomNotFoundError(invite_code)
        return self.get_room(room_row["room_id"])

    def update_room(self, room_id: str, payload: UpdateRoomRequest) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE rooms
                SET title = ?, last_activity_at = ?
                WHERE room_id = ?
                """,
                (payload.title.strip(), datetime.now(UTC).isoformat(), room_id),
            )
            if not cursor.rowcount:
                raise RoomNotFoundError(room_id)
        return self.get_room(room_id)

    def get_participant(self, room_id: str, participant_id: str) -> RoomParticipant:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = ? AND participant_id = ? AND left_at IS NULL
                """,
                (room_id, participant_id),
            ).fetchone()
        if row is None:
            raise RoomNotFoundError(participant_id)
        return _participant_from_row(row)

    def join_room(
        self,
        room_id: str,
        payload: JoinRoomRequest,
        participant_id: str | None = None,
        user_id: str | None = None,
    ) -> RoomDetail:
        self.cleanup_expired_rooms()
        reactivated_existing = False
        with self._connect() as connection:
            room_row = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = ?",
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)

            participant_rows = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = ?
                  AND left_at IS NULL
                ORDER BY joined_at ASC
                """,
                (room_id,),
            ).fetchall()
            resolved_display_name = payload.display_name.strip()
            if user_id is None and not participant_id:
                guest_name_rows = connection.execute(
                    """
                    SELECT display_name
                    FROM participants
                    WHERE room_id = ?
                      AND user_id IS NULL
                    """,
                    (room_id,),
                ).fetchall()
                resolved_display_name = _next_guest_display_name(
                    [row["display_name"] for row in guest_name_rows]
                )
            existing_row = None
            if participant_id:
                existing_row = connection.execute(
                    """
                    SELECT participant_id, user_id, left_at
                    FROM participants
                    WHERE room_id = ? AND participant_id = ?
                    """,
                    (room_id, participant_id),
                ).fetchone()
            elif user_id:
                existing_row = connection.execute(
                    """
                    SELECT participant_id, user_id, left_at
                    FROM participants
                    WHERE room_id = ? AND user_id = ?
                    ORDER BY joined_at DESC
                    LIMIT 1
                    """,
                    (room_id, user_id),
                ).fetchone()
            if existing_row is not None:
                if existing_row["left_at"] is not None and len(participant_rows) >= self.max_participants:
                    raise RoomCapacityError(room_id)
                duplicate_cleanup_at = datetime.now(UTC).isoformat()
                connection.execute(
                    """
                    UPDATE participants
                    SET user_id = ?, display_name = ?, icon = ?, language = ?, left_at = NULL
                    WHERE participant_id = ?
                    """,
                    (
                        user_id or existing_row["user_id"],
                        resolved_display_name,
                        (payload.icon or "").strip(),
                        payload.language,
                        existing_row["participant_id"],
                    ),
                )
                if user_id:
                    connection.execute(
                        """
                        UPDATE participants
                        SET left_at = ?
                        WHERE room_id = ?
                          AND user_id = ?
                          AND participant_id <> ?
                          AND left_at IS NULL
                        """,
                        (
                            duplicate_cleanup_at,
                            room_id,
                            user_id,
                            existing_row["participant_id"],
                        ),
                    )
                active_count = connection.execute(
                    """
                    SELECT COUNT(*) AS participant_count
                    FROM participants
                    WHERE room_id = ? AND left_at IS NULL
                    """,
                    (room_id,),
                ).fetchone()["participant_count"]
                connection.execute(
                    "UPDATE rooms SET status = ?, last_activity_at = ? WHERE room_id = ?",
                    (
                        self._derive_status(active_count),
                        datetime.now(UTC).isoformat(),
                        room_id,
                    ),
                )
                reactivated_existing = True
            if reactivated_existing:
                pass
            elif len(participant_rows) >= self.max_participants:
                raise RoomCapacityError(room_id)
            else:
                participant = RoomParticipant(
                    participant_id=self._generate_participant_id(),
                    user_id=user_id,
                    display_name=resolved_display_name,
                    icon=(payload.icon or "").strip(),
                    language=payload.language,
                )
                connection.execute(
                    """
                    INSERT INTO participants (participant_id, room_id, user_id, display_name, icon, language, joined_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        participant.participant_id,
                        room_id,
                        participant.user_id,
                        participant.display_name,
                        participant.icon,
                        participant.language,
                        participant.joined_at.isoformat(),
                    ),
                )
                connection.execute(
                    "UPDATE rooms SET status = ? WHERE room_id = ?",
                    (self._derive_status(len(participant_rows) + 1), room_id),
                )
                connection.execute(
                    "UPDATE rooms SET last_activity_at = ? WHERE room_id = ?",
                    (datetime.now(UTC).isoformat(), room_id),
                )
        return self.get_room(room_id)

    def leave_room(self, room_id: str, participant_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = ?",
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)
            cursor = connection.execute(
                """
                UPDATE participants
                SET left_at = ?
                WHERE room_id = ? AND participant_id = ? AND left_at IS NULL
                """,
                (datetime.now(UTC).isoformat(), room_id, participant_id),
            )
            if not cursor.rowcount:
                raise RoomNotFoundError(participant_id)
            participant_count = connection.execute(
                """
                SELECT COUNT(*) AS participant_count
                FROM participants
                WHERE room_id = ? AND left_at IS NULL
                """,
                (room_id,),
            ).fetchone()["participant_count"]
            connection.execute(
                "UPDATE rooms SET status = ?, last_activity_at = ? WHERE room_id = ?",
                (
                    self._derive_status(participant_count),
                    datetime.now(UTC).isoformat(),
                    room_id,
                ),
            )
        return self.get_room(room_id)

    def list_turns(self, room_id: str) -> list[RoomTurn]:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_exists = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = ?",
                (room_id,),
            ).fetchone()
            if room_exists is None:
                raise RoomNotFoundError(room_id)

            rows = connection.execute(
                """
                SELECT
                    turns.turn_id,
                    turns.room_id,
                    turns.source_language,
                    turns.source_text,
                    turns.translations_json,
                    turns.turn_type,
                    turns.attachment_name,
                    turns.attachment_url,
                    turns.attachment_content_type,
                    turns.attachment_size_bytes,
                    turns.delivery,
                    turns.created_at,
                    participants.participant_id,
                    participants.user_id,
                    participants.display_name,
                    participants.icon,
                    participants.language,
                    participants.joined_at
                FROM turns
                JOIN participants ON participants.participant_id = turns.participant_id
                WHERE turns.room_id = ?
                ORDER BY turns.created_at ASC
                """,
                (room_id,),
            ).fetchall()
        return [_turn_from_row(row) for row in rows]

    def add_turn(
        self,
        room_id: str,
        participant: RoomParticipant,
        source_language: str,
        source_text: str,
        translations: dict[str, str],
        delivery: str,
        turn_type: str = "text",
        attachment: RoomAttachment | None = None,
    ) -> RoomTurn:
        self.cleanup_expired_rooms()
        turn = RoomTurn(
            turn_id=self._generate_turn_id(),
            room_id=room_id,
            speaker=participant,
            source_language=source_language,
            source_text=source_text,
            translations=dict(translations),
            turn_type=turn_type,
            attachment=attachment,
            delivery=delivery,
        )
        with self._connect() as connection:
            room_exists = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = ?",
                (room_id,),
            ).fetchone()
            if room_exists is None:
                raise RoomNotFoundError(room_id)
            connection.execute(
                """
                INSERT INTO turns (
                    turn_id, room_id, participant_id, source_language, source_text,
                    translations_json, turn_type, attachment_name, attachment_url,
                    attachment_content_type, attachment_size_bytes, delivery, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn.turn_id,
                    room_id,
                    participant.participant_id,
                    turn.source_language,
                    turn.source_text,
                    json.dumps(turn.translations, ensure_ascii=False),
                    turn.turn_type,
                    turn.attachment.file_name if turn.attachment else "",
                    turn.attachment.file_url if turn.attachment else "",
                    turn.attachment.content_type if turn.attachment else "",
                    turn.attachment.size_bytes if turn.attachment else 0,
                    turn.delivery,
                    turn.created_at.isoformat(),
                ),
            )
            connection.execute(
                "UPDATE rooms SET last_activity_at = ? WHERE room_id = ?",
                (turn.created_at.isoformat(), room_id),
            )
        return turn

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

    def _derive_status(self, participant_count: int) -> RoomStatus:
        return "ready" if participant_count >= 2 else "waiting"

    def _generate_room_id(self) -> str:
        while True:
            room_id = f"room_{secrets.token_hex(8)}"
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT room_id FROM rooms WHERE room_id = ?",
                    (room_id,),
                ).fetchone()
            if row is None:
                return room_id

    def _generate_invite_code(self, connection: sqlite3.Connection | None = None) -> str:
        while True:
            invite_code = secrets.token_urlsafe(9)
            if connection is None:
                with self._connect() as managed_connection:
                    row = managed_connection.execute(
                        "SELECT room_id FROM rooms WHERE invite_code = ?",
                        (invite_code,),
                    ).fetchone()
            else:
                row = connection.execute(
                    "SELECT room_id FROM rooms WHERE invite_code = ?",
                    (invite_code,),
                ).fetchone()
            if row is None:
                return invite_code

    def _generate_participant_id(self) -> str:
        return secrets.token_hex(6)

    def _generate_turn_id(self) -> str:
        return secrets.token_hex(8)

    def _prune_expired_rooms(self) -> int:
        cutoff = (datetime.now(UTC) - timedelta(minutes=self.ttl_minutes)).isoformat()
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM rooms WHERE last_activity_at < ?", (cutoff,))
        return cursor.rowcount if cursor.rowcount != -1 else 0


class PostgresRoomStore(RoomStore):
    def __init__(self, db_url: str, max_participants: int = 2, ttl_minutes: int = 1440) -> None:
        self.db_url = db_url
        self.max_participants = max(max_participants, 2)
        self.ttl_minutes = max(ttl_minutes, 1)

    def initialize(self) -> None:
        _require_psycopg()
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id TEXT PRIMARY KEY,
                    invite_code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    creator_participant_id TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    last_activity_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            room_columns = {
                row["column_name"]
                for row in connection.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'rooms'
                    """
                ).fetchall()
            }
            if "creator_participant_id" not in room_columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN creator_participant_id TEXT"
                )
            if "invite_code" not in room_columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN invite_code TEXT NOT NULL DEFAULT ''"
                )
                room_id_rows = connection.execute(
                    "SELECT room_id FROM rooms WHERE invite_code = ''"
                ).fetchall()
                for row in room_id_rows:
                    connection.execute(
                        "UPDATE rooms SET invite_code = %s WHERE room_id = %s",
                        (self._generate_invite_code(connection), row["room_id"]),
                    )
            if "title" not in room_columns:
                connection.execute(
                    "ALTER TABLE rooms ADD COLUMN title TEXT NOT NULL DEFAULT ''"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    participant_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
                    display_name TEXT NOT NULL,
                    icon TEXT NOT NULL DEFAULT '',
                    language TEXT NOT NULL,
                    joined_at TIMESTAMPTZ NOT NULL,
                    left_at TIMESTAMPTZ
                )
                """
            )
            columns = {
                row["column_name"]
                for row in connection.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'participants'
                    """
                ).fetchall()
            }
            if "icon" not in columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN icon TEXT NOT NULL DEFAULT ''"
                )
            if "left_at" not in columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN left_at TIMESTAMPTZ"
                )
            if "user_id" not in columns:
                connection.execute(
                    "ALTER TABLE participants ADD COLUMN user_id TEXT"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
                    participant_id TEXT NOT NULL REFERENCES participants(participant_id) ON DELETE CASCADE,
                    source_language TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translations_json JSONB NOT NULL,
                    turn_type TEXT NOT NULL DEFAULT 'text',
                    attachment_name TEXT NOT NULL DEFAULT '',
                    attachment_url TEXT NOT NULL DEFAULT '',
                    attachment_content_type TEXT NOT NULL DEFAULT '',
                    attachment_size_bytes BIGINT NOT NULL DEFAULT 0,
                    delivery TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            turn_columns = {
                row["column_name"]
                for row in connection.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'turns'
                    """
                ).fetchall()
            }
            if "turn_type" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN turn_type TEXT NOT NULL DEFAULT 'text'"
                )
            if "attachment_name" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_name TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_url" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_url TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_content_type" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_content_type TEXT NOT NULL DEFAULT ''"
                )
            if "attachment_size_bytes" not in turn_columns:
                connection.execute(
                    "ALTER TABLE turns ADD COLUMN attachment_size_bytes BIGINT NOT NULL DEFAULT 0"
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_participants_room_id ON participants(room_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_turns_room_id ON turns(room_id, created_at)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_rooms_last_activity ON rooms(last_activity_at)"
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_rooms_invite_code ON rooms(invite_code)"
            )

    def list_rooms(self) -> list[RoomSummary]:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    rooms.room_id,
                    rooms.invite_code,
                    rooms.title,
                    rooms.status,
                    rooms.creator_participant_id,
                    rooms.created_at,
                    rooms.last_activity_at,
                    COUNT(participants.participant_id) AS participant_count
                FROM rooms
                LEFT JOIN participants
                    ON participants.room_id = rooms.room_id
                   AND participants.left_at IS NULL
                GROUP BY rooms.room_id
                ORDER BY rooms.created_at DESC
                """
            ).fetchall()
        return [
            RoomSummary(
                room_id=row["room_id"],
                invite_code=row["invite_code"],
                title=row["title"] or "",
                status=row["status"],
                participant_count=row["participant_count"],
                creator_participant_id=row["creator_participant_id"],
                created_at=_parse_datetime(row["created_at"]),
                last_activity_at=_parse_datetime(row["last_activity_at"]),
            )
            for row in rows
        ]

    def cleanup_expired_rooms(self) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=self.ttl_minutes)
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM rooms WHERE last_activity_at < %s",
                (cutoff,),
            )
        return cursor.rowcount if cursor.rowcount != -1 else 0

    def create_room(self, payload: CreateRoomRequest, user_id: str | None = None) -> RoomDetail:
        room_id = self._generate_room_id()
        invite_code = self._generate_invite_code()
        participant = RoomParticipant(
            participant_id=self._generate_participant_id(),
            user_id=user_id,
            display_name=payload.display_name.strip(),
            icon=(payload.icon or "").strip(),
            language=payload.language,
        )
        created_at = datetime.now(UTC)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO rooms (room_id, invite_code, title, status, creator_participant_id, created_at, last_activity_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (room_id, invite_code, payload.title.strip(), "waiting", participant.participant_id, created_at, created_at),
            )
            connection.execute(
                """
                INSERT INTO participants (participant_id, room_id, user_id, display_name, icon, language, joined_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    participant.participant_id,
                    room_id,
                    participant.user_id,
                    participant.display_name,
                    participant.icon,
                    participant.language,
                    participant.joined_at,
                ),
            )
        return self.get_room(room_id)

    def get_room(self, room_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                """
                SELECT room_id, invite_code, title, status, creator_participant_id, created_at, last_activity_at
                FROM rooms
                WHERE room_id = %s
                """,
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)

            participant_rows = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = %s
                  AND left_at IS NULL
                ORDER BY joined_at ASC
                """,
                (room_id,),
            ).fetchall()

            participant_count = len(participant_rows)
            derived_status = self._derive_status(participant_count)
            if room_row["status"] != derived_status:
                connection.execute(
                    "UPDATE rooms SET status = %s WHERE room_id = %s",
                    (derived_status, room_id),
                )

        participants = [_participant_from_row(row) for row in participant_rows]
        return RoomDetail(
            room_id=room_row["room_id"],
            invite_code=room_row["invite_code"],
            title=room_row["title"] or "",
            status=derived_status,
            participant_count=participant_count,
            creator_participant_id=room_row["creator_participant_id"],
            created_at=_parse_datetime(room_row["created_at"]),
            last_activity_at=_parse_datetime(room_row["last_activity_at"]),
            participants=participants,
        )

    def get_room_by_invite_code(self, invite_code: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                """
                SELECT room_id
                FROM rooms
                WHERE invite_code = %s
                """,
                (invite_code,),
            ).fetchone()
        if room_row is None:
            raise RoomNotFoundError(invite_code)
        return self.get_room(room_row["room_id"])

    def update_room(self, room_id: str, payload: UpdateRoomRequest) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE rooms
                SET title = %s, last_activity_at = %s
                WHERE room_id = %s
                """,
                (payload.title.strip(), datetime.now(UTC), room_id),
            )
            if not cursor.rowcount:
                raise RoomNotFoundError(room_id)
        return self.get_room(room_id)

    def get_participant(self, room_id: str, participant_id: str) -> RoomParticipant:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = %s AND participant_id = %s AND left_at IS NULL
                """,
                (room_id, participant_id),
            ).fetchone()
        if row is None:
            raise RoomNotFoundError(participant_id)
        return _participant_from_row(row)

    def join_room(
        self,
        room_id: str,
        payload: JoinRoomRequest,
        participant_id: str | None = None,
        user_id: str | None = None,
    ) -> RoomDetail:
        self.cleanup_expired_rooms()
        reactivated_existing = False
        with self._connect() as connection:
            room_row = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = %s",
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)

            participant_rows = connection.execute(
                """
                SELECT participant_id, user_id, display_name, icon, language, joined_at
                FROM participants
                WHERE room_id = %s
                  AND left_at IS NULL
                ORDER BY joined_at ASC
                """,
                (room_id,),
            ).fetchall()
            resolved_display_name = payload.display_name.strip()
            if user_id is None and not participant_id:
                guest_name_rows = connection.execute(
                    """
                    SELECT display_name
                    FROM participants
                    WHERE room_id = %s
                      AND user_id IS NULL
                    """,
                    (room_id,),
                ).fetchall()
                resolved_display_name = _next_guest_display_name(
                    [row["display_name"] for row in guest_name_rows]
                )
            existing_row = None
            if participant_id:
                existing_row = connection.execute(
                    """
                    SELECT participant_id, user_id, left_at
                    FROM participants
                    WHERE room_id = %s AND participant_id = %s
                    """,
                    (room_id, participant_id),
                ).fetchone()
            elif user_id:
                existing_row = connection.execute(
                    """
                    SELECT participant_id, user_id, left_at
                    FROM participants
                    WHERE room_id = %s AND user_id = %s
                    ORDER BY joined_at DESC
                    LIMIT 1
                    """,
                    (room_id, user_id),
                ).fetchone()
            if existing_row is not None:
                if existing_row["left_at"] is not None and len(participant_rows) >= self.max_participants:
                    raise RoomCapacityError(room_id)
                duplicate_cleanup_at = datetime.now(UTC)
                connection.execute(
                    """
                    UPDATE participants
                    SET user_id = %s, display_name = %s, icon = %s, language = %s, left_at = NULL
                    WHERE participant_id = %s
                    """,
                    (
                        user_id or existing_row["user_id"],
                        resolved_display_name,
                        (payload.icon or "").strip(),
                        payload.language,
                        existing_row["participant_id"],
                    ),
                )
                if user_id:
                    connection.execute(
                        """
                        UPDATE participants
                        SET left_at = %s
                        WHERE room_id = %s
                          AND user_id = %s
                          AND participant_id <> %s
                          AND left_at IS NULL
                        """,
                        (
                            duplicate_cleanup_at,
                            room_id,
                            user_id,
                            existing_row["participant_id"],
                        ),
                    )
                active_count = connection.execute(
                    """
                    SELECT COUNT(*) AS participant_count
                    FROM participants
                    WHERE room_id = %s AND left_at IS NULL
                    """,
                    (room_id,),
                ).fetchone()["participant_count"]
                connection.execute(
                    "UPDATE rooms SET status = %s, last_activity_at = %s WHERE room_id = %s",
                    (self._derive_status(active_count), datetime.now(UTC), room_id),
                )
                reactivated_existing = True
            if reactivated_existing:
                pass
            elif len(participant_rows) >= self.max_participants:
                raise RoomCapacityError(room_id)
            else:
                participant = RoomParticipant(
                    participant_id=self._generate_participant_id(),
                    user_id=user_id,
                    display_name=resolved_display_name,
                    icon=(payload.icon or "").strip(),
                    language=payload.language,
                )
                connection.execute(
                    """
                    INSERT INTO participants (participant_id, room_id, user_id, display_name, icon, language, joined_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        participant.participant_id,
                        room_id,
                        participant.user_id,
                        participant.display_name,
                        participant.icon,
                        participant.language,
                        participant.joined_at,
                    ),
                )
                connection.execute(
                    "UPDATE rooms SET status = %s, last_activity_at = %s WHERE room_id = %s",
                    (self._derive_status(len(participant_rows) + 1), datetime.now(UTC), room_id),
                )
        return self.get_room(room_id)

    def leave_room(self, room_id: str, participant_id: str) -> RoomDetail:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_row = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = %s",
                (room_id,),
            ).fetchone()
            if room_row is None:
                raise RoomNotFoundError(room_id)
            cursor = connection.execute(
                """
                UPDATE participants
                SET left_at = %s
                WHERE room_id = %s AND participant_id = %s AND left_at IS NULL
                """,
                (datetime.now(UTC), room_id, participant_id),
            )
            if not cursor.rowcount:
                raise RoomNotFoundError(participant_id)
            participant_count = connection.execute(
                """
                SELECT COUNT(*) AS participant_count
                FROM participants
                WHERE room_id = %s AND left_at IS NULL
                """,
                (room_id,),
            ).fetchone()["participant_count"]
            connection.execute(
                "UPDATE rooms SET status = %s, last_activity_at = %s WHERE room_id = %s",
                (self._derive_status(participant_count), datetime.now(UTC), room_id),
            )
        return self.get_room(room_id)

    def list_turns(self, room_id: str) -> list[RoomTurn]:
        self.cleanup_expired_rooms()
        with self._connect() as connection:
            room_exists = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = %s",
                (room_id,),
            ).fetchone()
            if room_exists is None:
                raise RoomNotFoundError(room_id)

            rows = connection.execute(
                """
                SELECT
                    turns.turn_id,
                    turns.room_id,
                    turns.source_language,
                    turns.source_text,
                    turns.translations_json,
                    turns.turn_type,
                    turns.attachment_name,
                    turns.attachment_url,
                    turns.attachment_content_type,
                    turns.attachment_size_bytes,
                    turns.delivery,
                    turns.created_at,
                    participants.participant_id,
                    participants.user_id,
                    participants.display_name,
                    participants.icon,
                    participants.language,
                    participants.joined_at
                FROM turns
                JOIN participants ON participants.participant_id = turns.participant_id
                WHERE turns.room_id = %s
                ORDER BY turns.created_at ASC
                """,
                (room_id,),
            ).fetchall()
        return [_turn_from_row(row) for row in rows]

    def add_turn(
        self,
        room_id: str,
        participant: RoomParticipant,
        source_language: str,
        source_text: str,
        translations: dict[str, str],
        delivery: str,
        turn_type: str = "text",
        attachment: RoomAttachment | None = None,
    ) -> RoomTurn:
        self.cleanup_expired_rooms()
        turn = RoomTurn(
            turn_id=self._generate_turn_id(),
            room_id=room_id,
            speaker=participant,
            source_language=source_language,
            source_text=source_text,
            translations=dict(translations),
            turn_type=turn_type,
            attachment=attachment,
            delivery=delivery,
        )
        with self._connect() as connection:
            room_exists = connection.execute(
                "SELECT room_id FROM rooms WHERE room_id = %s",
                (room_id,),
            ).fetchone()
            if room_exists is None:
                raise RoomNotFoundError(room_id)
            connection.execute(
                """
                INSERT INTO turns (
                    turn_id, room_id, participant_id, source_language, source_text,
                    translations_json, turn_type, attachment_name, attachment_url,
                    attachment_content_type, attachment_size_bytes, delivery, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    turn.turn_id,
                    room_id,
                    participant.participant_id,
                    turn.source_language,
                    turn.source_text,
                    json.dumps(turn.translations, ensure_ascii=False),
                    turn.turn_type,
                    turn.attachment.file_name if turn.attachment else "",
                    turn.attachment.file_url if turn.attachment else "",
                    turn.attachment.content_type if turn.attachment else "",
                    turn.attachment.size_bytes if turn.attachment else 0,
                    turn.delivery,
                    turn.created_at,
                ),
            )
            connection.execute(
                "UPDATE rooms SET last_activity_at = %s WHERE room_id = %s",
                (turn.created_at, room_id),
            )
        return turn

    def _connect(self):
        _require_psycopg()
        return psycopg.connect(self.db_url, row_factory=dict_row)

    def _derive_status(self, participant_count: int) -> RoomStatus:
        return "ready" if participant_count >= 2 else "waiting"

    def _generate_room_id(self) -> str:
        while True:
            room_id = f"room_{secrets.token_hex(8)}"
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT room_id FROM rooms WHERE room_id = %s",
                    (room_id,),
                ).fetchone()
            if row is None:
                return room_id

    def _generate_invite_code(self, connection: Any | None = None) -> str:
        while True:
            invite_code = secrets.token_urlsafe(9)
            if connection is None:
                with self._connect() as managed_connection:
                    row = managed_connection.execute(
                        "SELECT room_id FROM rooms WHERE invite_code = %s",
                        (invite_code,),
                    ).fetchone()
            else:
                row = connection.execute(
                    "SELECT room_id FROM rooms WHERE invite_code = %s",
                    (invite_code,),
                ).fetchone()
            if row is None:
                return invite_code

    def _generate_participant_id(self) -> str:
        return secrets.token_hex(6)

    def _generate_turn_id(self) -> str:
        return secrets.token_hex(8)


def _participant_from_row(row: Any) -> RoomParticipant:
    return RoomParticipant(
        participant_id=row["participant_id"],
        user_id=row["user_id"] if "user_id" in row.keys() else None,
        display_name=row["display_name"],
        icon=row.get("icon", "") if hasattr(row, "get") else row["icon"],
        language=row["language"],
        joined_at=_parse_datetime(row["joined_at"]),
    )


def _turn_from_row(row: Any) -> RoomTurn:
    translations = row["translations_json"]
    if isinstance(translations, str):
        translations = json.loads(translations)
    attachment_name = row["attachment_name"] if "attachment_name" in row.keys() else ""
    attachment_url = row["attachment_url"] if "attachment_url" in row.keys() else ""
    attachment_content_type = (
        row["attachment_content_type"] if "attachment_content_type" in row.keys() else ""
    )
    attachment_size_bytes = (
        row["attachment_size_bytes"] if "attachment_size_bytes" in row.keys() else 0
    )
    attachment = None
    if attachment_name and attachment_url:
        attachment = RoomAttachment(
            file_name=attachment_name,
            file_url=attachment_url,
            content_type=attachment_content_type or "application/octet-stream",
            size_bytes=attachment_size_bytes or 0,
        )
    return RoomTurn(
        turn_id=row["turn_id"],
        room_id=row["room_id"],
        speaker=_participant_from_row(row),
        source_language=row["source_language"],
        source_text=row["source_text"],
        translations=translations,
        turn_type=row["turn_type"] if "turn_type" in row.keys() else "text",
        attachment=attachment,
        delivery=row["delivery"],
        created_at=_parse_datetime(row["created_at"]),
    )


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _require_psycopg() -> None:
    if psycopg is None or dict_row is None:
        raise RuntimeError(
            "Postgres room storage requires psycopg. Install it with `pip install .[postgres]`."
        )


@lru_cache(maxsize=8)
def get_room_store(
    backend: str = "sqlite",
    db_path: str = "data/bunny_app.sqlite3",
    db_url: str | None = None,
    max_participants: int = 2,
    ttl_minutes: int = 1440,
) -> RoomStore:
    if backend == "memory":
        store = InMemoryRoomStore(max_participants=max_participants, ttl_minutes=ttl_minutes)
    elif backend == "sqlite":
        store = SQLiteRoomStore(db_path=db_path, max_participants=max_participants, ttl_minutes=ttl_minutes)
    elif backend == "postgres":
        if not db_url:
            raise RuntimeError(
                "Postgres room storage requires `BUNNY_ROOM_STORE_URL` to be configured."
            )
        store = PostgresRoomStore(
            db_url=db_url,
            max_participants=max_participants,
            ttl_minutes=ttl_minutes,
        )
    else:
        raise ValueError(f"Unsupported room store backend: {backend}")
    store.initialize()
    return store
