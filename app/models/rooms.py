from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


SupportedLanguage = Literal["ko", "es", "auto"]
RoomStatus = Literal["waiting", "ready", "active", "ended"]


class RoomParticipant(BaseModel):
    participant_id: str
    user_id: str | None = None
    display_name: str
    icon: str = ""
    language: SupportedLanguage
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RoomSummary(BaseModel):
    room_id: str
    invite_code: str | None = None
    title: str = ""
    status: RoomStatus
    participant_count: int
    creator_participant_id: str | None = None
    created_at: datetime
    last_activity_at: datetime


class RoomDetail(RoomSummary):
    participants: list[RoomParticipant] = Field(default_factory=list)


class InviteRoomPreview(BaseModel):
    room_id: str
    invite_code: str
    status: RoomStatus
    participant_count: int
    created_at: datetime
    last_activity_at: datetime
    participants: list[RoomParticipant] = Field(default_factory=list)


class RoomCleanupResult(BaseModel):
    cleaned_rooms: int


class CreateDemoTurnRequest(BaseModel):
    participant_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1, max_length=2000)
    language: SupportedLanguage | None = None


class RoomAttachment(BaseModel):
    file_name: str
    file_url: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0


class RoomTurn(BaseModel):
    turn_id: str
    room_id: str
    speaker: RoomParticipant
    source_language: SupportedLanguage
    source_text: str
    translations: dict[str, str] = Field(default_factory=dict)
    turn_type: Literal["text", "attachment"] = "text"
    attachment: RoomAttachment | None = None
    delivery: Literal["realtime", "upload", "demo", "attachment"] = "realtime"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CreateRoomRequest(BaseModel):
    display_name: str = Field(default="Host", min_length=1, max_length=40)
    icon: str = Field(default="", max_length=80)
    title: str = Field(default="", max_length=80)
    language: SupportedLanguage


class JoinRoomRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    icon: str = Field(default="", max_length=80)
    language: SupportedLanguage


class UpdateRoomRequest(BaseModel):
    title: str = Field(default="", max_length=80)
