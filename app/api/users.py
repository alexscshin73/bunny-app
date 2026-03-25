from datetime import UTC, datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.deps.auth import get_current_user, get_optional_current_user, get_user_store
from app.models.rooms import RoomTurn
from app.models.users import (
    AuthSessionResponse,
    CreateAnnouncementNotificationRequest,
    DeleteWebPushSubscriptionRequest,
    DeleteHistoryResponse,
    LoginUserRequest,
    NotificationReadAllResponse,
    NotificationReadResponse,
    RegisterUserRequest,
    SaveWebPushSubscriptionRequest,
    UpdateProfileRequest,
    UserNotification,
    UserProfile,
    UserRoomDetail,
    UserRoomSummary,
    WebPushConfigResponse,
)
from app.services.rooms import RoomNotFoundError, get_room_store
from app.services.users import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    InvalidCredentialsError,
    RoomHistoryNotFoundError,
    SQLiteUserStore,
    UserAlreadyExistsError,
)
from app.services.web_push import send_web_push_notification, web_push_is_configured

router = APIRouter(tags=["users"])


def _write_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=SESSION_MAX_AGE_SECONDS,
        expires=SESSION_MAX_AGE_SECONDS,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


@router.post("/api/auth/register", response_model=AuthSessionResponse)
async def register_user(
    payload: RegisterUserRequest,
    response: Response,
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> AuthSessionResponse:
    try:
        user = user_store.register_user(
            display_name=payload.display_name,
            phone=payload.phone,
            icon=payload.icon,
            bio=payload.bio,
            preferred_language=payload.preferred_language,
            notifications_enabled=payload.notifications_enabled,
            password=payload.password,
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number is already registered.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    session_token = user_store.create_session(user.user_id)
    _write_session_cookie(response, session_token)
    return AuthSessionResponse(user=user)


@router.post("/api/auth/login", response_model=AuthSessionResponse)
async def login_user(
    payload: LoginUserRequest,
    response: Response,
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> AuthSessionResponse:
    try:
        user = user_store.authenticate(payload.phone, payload.password)
    except (InvalidCredentialsError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phone number or password is incorrect.",
        ) from exc

    session_token = user_store.create_session(user.user_id)
    _write_session_cookie(response, session_token)
    return AuthSessionResponse(user=user)


@router.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    user: UserProfile | None = Depends(get_optional_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> Response:
    del user
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    user_store.delete_session(session_token or "")
    _clear_session_cookie(response)
    return response


@router.get("/api/auth/me", response_model=AuthSessionResponse)
async def get_me(user: UserProfile = Depends(get_current_user)) -> AuthSessionResponse:
    return AuthSessionResponse(user=user)


def _apply_profile_update(
    payload: UpdateProfileRequest,
    user: UserProfile,
    user_store: SQLiteUserStore,
) -> AuthSessionResponse:
    try:
        updated_user = user_store.update_user(
            user.user_id,
            display_name=payload.display_name,
            icon=payload.icon,
            bio=payload.bio,
            preferred_language=payload.preferred_language,
            notifications_enabled=payload.notifications_enabled,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AuthSessionResponse(user=updated_user)


@router.patch("/api/auth/me", response_model=AuthSessionResponse)
async def update_me_patch(
    payload: UpdateProfileRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> AuthSessionResponse:
    return _apply_profile_update(payload, user, user_store)


@router.put("/api/auth/me", response_model=AuthSessionResponse)
async def update_me_put(
    payload: UpdateProfileRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> AuthSessionResponse:
    return _apply_profile_update(payload, user, user_store)


@router.post("/api/auth/me", response_model=AuthSessionResponse)
async def update_me_post(
    payload: UpdateProfileRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> AuthSessionResponse:
    return _apply_profile_update(payload, user, user_store)


@router.get("/api/me/rooms", response_model=list[UserRoomSummary])
async def list_my_rooms(
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> list[UserRoomSummary]:
    return user_store.list_room_history(user.user_id)


@router.get("/api/me/rooms/{room_id}", response_model=UserRoomDetail)
async def get_my_room_detail(
    room_id: str,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> UserRoomDetail:
    settings = get_settings()
    room_store = get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )
    try:
        participant_id, joined_at = user_store.get_room_membership(user.user_id, room_id)
        room = room_store.get_room(room_id)
        turns = room_store.list_turns(room_id)
    except RoomHistoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room history not found.") from exc
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.") from exc
    return UserRoomDetail(joined_at=joined_at, participant_id=participant_id, room=room, turns=turns)


@router.delete("/api/me/rooms/{room_id}", response_model=DeleteHistoryResponse)
async def delete_my_room_history(
    room_id: str,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> DeleteHistoryResponse:
    deleted = user_store.delete_room_history(user.user_id, room_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room history not found.")
    return DeleteHistoryResponse(room_id=room_id)


@router.get("/api/me/notifications", response_model=list[UserNotification])
async def list_my_notifications(
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> list[UserNotification]:
    if not user.notifications_enabled:
        return []
    return user_store.list_notifications(user.user_id)


@router.post("/api/me/notifications/read-all", response_model=NotificationReadAllResponse)
async def read_all_my_notifications(
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> NotificationReadAllResponse:
    updated_count = user_store.mark_all_notifications_read(user.user_id)
    return NotificationReadAllResponse(updated_count=updated_count)


@router.post("/api/me/notifications/{notification_id}/read", response_model=NotificationReadResponse)
async def read_my_notification(
    notification_id: str,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> NotificationReadResponse:
    updated = user_store.mark_notification_read(user.user_id, notification_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return NotificationReadResponse(notification_id=notification_id)


@router.post("/api/me/notifications/announcements", response_model=UserNotification, status_code=status.HTTP_201_CREATED)
async def create_my_announcement_notification(
    payload: CreateAnnouncementNotificationRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> UserNotification:
    if not user.notifications_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Notifications are turned off.")
    notification = user_store.create_notification(
        user.user_id,
        "announcement",
        payload.title,
        payload.body,
        room_id=payload.room_id,
        room_title=payload.room_title,
        actor_name="Bunny",
        metadata={"source": "manual_announcement"},
    )
    send_web_push_notification(get_settings(), user_store, user.user_id, notification)
    return notification


@router.get("/api/me/web-push/config", response_model=WebPushConfigResponse)
async def get_my_web_push_config(
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> WebPushConfigResponse:
    del user, user_store
    settings = get_settings()
    configured = bool(
        settings.web_push_public_key and settings.web_push_private_key and settings.web_push_subject
    )
    enabled = web_push_is_configured(settings)
    return WebPushConfigResponse(
        enabled=enabled,
        configured=configured,
        supported=enabled,
        public_key=settings.web_push_public_key if enabled else None,
    )


@router.post("/api/me/web-push/subscriptions", status_code=status.HTTP_204_NO_CONTENT)
async def save_my_web_push_subscription(
    payload: SaveWebPushSubscriptionRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> Response:
    user_store.save_push_subscription(user.user_id, payload.subscription)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/api/me/web-push/subscriptions", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_web_push_subscription(
    payload: DeleteWebPushSubscriptionRequest,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> Response:
    user_store.delete_push_subscription(user.user_id, payload.endpoint)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _format_turn_download(turns: list[RoomTurn], room_id: str, exported_at: datetime) -> str:
    lines = [
        f"Bunny Room Export",
        f"Room ID: {room_id}",
        f"Exported At: {exported_at.astimezone(UTC).isoformat()}",
        "",
    ]
    for turn in turns:
        lines.append(
            f"[{turn.created_at.astimezone(UTC).isoformat()}] {turn.speaker.display_name} ({turn.source_language})"
        )
        if turn.turn_type == "attachment" and turn.attachment:
            lines.append(f"Attachment: {turn.attachment.file_name}")
            lines.append(f"URL: {turn.attachment.file_url}")
            lines.append(f"Content-Type: {turn.attachment.content_type}")
            lines.append(f"Size: {turn.attachment.size_bytes} bytes")
        else:
            lines.append(turn.source_text)
        for language, translation in turn.translations.items():
            lines.append(f"  -> {language}: {translation}")
        lines.append("")
    return "\n".join(lines)


@router.get("/api/me/rooms/{room_id}/download")
async def download_my_room_history(
    room_id: str,
    user: UserProfile = Depends(get_current_user),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> PlainTextResponse:
    settings = get_settings()
    room_store = get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )
    try:
        user_store.get_room_membership(user.user_id, room_id)
        turns = room_store.list_turns(room_id)
    except RoomHistoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room history not found.") from exc
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.") from exc

    export_text = _format_turn_download(turns, room_id, datetime.now(UTC))
    response = PlainTextResponse(export_text)
    response.headers["Content-Disposition"] = f'attachment; filename="{room_id}-history.txt"'
    return response
