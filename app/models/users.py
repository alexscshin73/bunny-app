from typing import Any, Literal

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.rooms import RoomDetail, RoomStatus, RoomTurn


UserPreferredLanguage = Literal["ko", "es"]
UserNotificationType = Literal["invite", "turn", "announcement"]


class UserProfile(BaseModel):
    user_id: str
    display_name: str
    phone: str
    icon: str = ""
    bio: str = ""
    preferred_language: UserPreferredLanguage | None = None
    notifications_enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_login_at: datetime | None = None


class RegisterUserRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    phone: str = Field(min_length=7, max_length=24)
    icon: str = Field(default="", max_length=80)
    bio: str = Field(default="", max_length=160)
    preferred_language: UserPreferredLanguage | None = None
    notifications_enabled: bool = True
    password: str = Field(min_length=4, max_length=128)


class LoginUserRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=24)
    password: str = Field(min_length=4, max_length=128)


class AuthSessionResponse(BaseModel):
    user: UserProfile


class UpdateProfileRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    icon: str = Field(default="", max_length=80)
    bio: str = Field(default="", max_length=160)
    preferred_language: UserPreferredLanguage | None = None
    notifications_enabled: bool = True


class UserRoomParticipantVisual(BaseModel):
    display_name: str
    icon: str = ""


class UserRoomSummary(BaseModel):
    room_id: str
    participant_id: str
    room_title: str = ""
    status: RoomStatus
    participant_count: int
    turn_count: int
    counterpart_name: str
    counterpart_icon: str = ""
    participant_visuals: list[UserRoomParticipantVisual] = Field(default_factory=list)
    last_message: str
    joined_at: datetime
    created_at: datetime
    last_activity_at: datetime


class UserRoomDetail(BaseModel):
    joined_at: datetime
    participant_id: str
    room: RoomDetail
    turns: list[RoomTurn] = Field(default_factory=list)


class DeleteHistoryResponse(BaseModel):
    room_id: str
    deleted: bool = True


class UserNotification(BaseModel):
    notification_id: str
    user_id: str
    notification_type: UserNotificationType
    title: str
    body: str
    room_id: str | None = None
    room_title: str = ""
    actor_user_id: str | None = None
    actor_name: str = ""
    actor_icon: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    read_at: datetime | None = None


class NotificationReadResponse(BaseModel):
    notification_id: str
    read: bool = True


class NotificationReadAllResponse(BaseModel):
    updated_count: int


class CreateAnnouncementNotificationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    body: str = Field(min_length=1, max_length=280)
    room_id: str | None = Field(default=None, max_length=80)
    room_title: str = Field(default="", max_length=80)


class WebPushSubscriptionKeys(BaseModel):
    auth: str = Field(min_length=1)
    p256dh: str = Field(min_length=1)


class WebPushSubscription(BaseModel):
    endpoint: str = Field(min_length=1)
    expirationTime: int | None = None
    keys: WebPushSubscriptionKeys


class SaveWebPushSubscriptionRequest(BaseModel):
    subscription: WebPushSubscription


class DeleteWebPushSubscriptionRequest(BaseModel):
    endpoint: str = Field(min_length=1)


class WebPushConfigResponse(BaseModel):
    enabled: bool
    configured: bool
    supported: bool
    public_key: str | None = None
