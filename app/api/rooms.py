from pathlib import Path
import secrets

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from app.config import Settings, get_settings
from app.deps.auth import get_user_store
from app.models.rooms import (
    CreateDemoTurnRequest,
    CreateRoomRequest,
    InviteRoomPreview,
    JoinRoomRequest,
    RoomAttachment,
    RoomCleanupResult,
    RoomDetail,
    RoomSummary,
    RoomTurn,
    UpdateRoomRequest,
)
from app.services.live_rooms import get_live_room_manager
from app.services.rooms import (
    RoomStore,
    RoomCapacityError,
    RoomNotFoundError,
    get_room_store,
)
from app.services.upload_turns import (
    UploadedAudioProcessingError,
    process_demo_text_turn,
    process_uploaded_audio_turn,
)
from app.services.users import SESSION_COOKIE_NAME, SQLiteUserStore
from app.services.users import RoomHistoryNotFoundError
from app.services.web_push import send_web_push_notification


GUEST_BUNNY_ICON = "bunny-guest"

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


def _attachment_upload_dir(settings: Settings, room_id: str) -> Path:
    room_dir = Path(settings.room_store_path).resolve().parent / "uploads" / room_id
    room_dir.mkdir(parents=True, exist_ok=True)
    return room_dir


def get_rooms_service(settings: Settings = Depends(get_settings)) -> RoomStore:
    return get_room_store(
        backend=settings.room_store_backend,
        db_path=settings.room_store_path,
        db_url=settings.room_store_url,
        max_participants=settings.room_max_participants,
        ttl_minutes=settings.room_ttl_minutes,
    )


def _display_room_title(room: RoomDetail) -> str:
    return room.title.strip() or f"Room {room.room_id}"


def _optional_user_store(settings: Settings) -> SQLiteUserStore | None:
    if settings.room_store_backend != "sqlite":
        return None
    store = SQLiteUserStore(settings.room_store_path)
    store.initialize()
    return store


def _create_invite_notification_for_joined_user(
    settings: Settings,
    user_store: SQLiteUserStore,
    current_user_id: str | None,
    invited_room: RoomDetail,
    resumed_participant_id: str | None,
) -> None:
    if not current_user_id or resumed_participant_id:
        return
    creator = next(
        (
            participant
            for participant in invited_room.participants
            if participant.participant_id == invited_room.creator_participant_id
        ),
        None,
    )
    if creator is None or creator.user_id == current_user_id:
        return
    if not user_store.user_notifications_enabled(current_user_id):
        return
    room_title = _display_room_title(invited_room)
    notification = user_store.create_notification(
        current_user_id,
        "invite",
        "Room invitation",
        f"{creator.display_name} invited you to {room_title}.",
        room_id=invited_room.room_id,
        room_title=room_title,
        actor_user_id=creator.user_id,
        actor_name=creator.display_name,
        actor_icon=creator.icon,
        metadata={"invite_code": invited_room.invite_code},
    )
    send_web_push_notification(settings, user_store, current_user_id, notification)


def _create_turn_notifications(
    settings: Settings,
    user_store: SQLiteUserStore,
    store: RoomStore,
    room_id: str,
    participant,
    turn: RoomTurn,
) -> None:
    target_user_ids = user_store.list_room_member_user_ids(room_id, exclude_user_id=participant.user_id)
    if not target_user_ids:
        return
    room = store.get_room(room_id)
    room_title = _display_room_title(room)
    if turn.turn_type == "attachment" and turn.attachment:
        body = f"{participant.display_name} sent {turn.attachment.file_name}."
    else:
        preview = turn.source_text.strip()
        if len(preview) > 80:
            preview = f"{preview[:77]}..."
        body = f"{participant.display_name}: {preview}"
    for user_id in target_user_ids:
        if not user_store.user_notifications_enabled(user_id):
            continue
        notification = user_store.create_notification(
            user_id,
            "turn",
            f"New message in {room_title}",
            body,
            room_id=room.room_id,
            room_title=room_title,
            actor_user_id=participant.user_id,
            actor_name=participant.display_name,
            actor_icon=participant.icon,
            metadata={
                "invite_code": room.invite_code,
                "turn_id": turn.turn_id,
                "turn_type": turn.turn_type,
                "delivery": turn.delivery,
            },
        )
        send_web_push_notification(settings, user_store, user_id, notification)


@router.get("", response_model=list[RoomSummary])
async def list_rooms(store: RoomStore = Depends(get_rooms_service)) -> list[RoomSummary]:
    return store.list_rooms()


@router.post("", response_model=RoomDetail, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: CreateRoomRequest,
    request: Request,
    store: RoomStore = Depends(get_rooms_service),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> RoomDetail:
    current_user = user_store.get_user_by_session(request.cookies.get(SESSION_COOKIE_NAME))
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to create a room.")
    payload = payload.model_copy(update={"icon": current_user.icon})
    room = store.create_room(payload, user_id=current_user.user_id)
    if current_user and room.participants:
        user_store.record_room_membership(
            current_user.user_id,
            room.room_id,
            room.participants[0].participant_id,
        )
    return room


@router.post("/_cleanup", response_model=RoomCleanupResult)
async def cleanup_rooms(store: RoomStore = Depends(get_rooms_service)) -> RoomCleanupResult:
    return RoomCleanupResult(cleaned_rooms=store.cleanup_expired_rooms())


@router.get("/invites/{invite_code}", response_model=InviteRoomPreview)
async def get_room_invite_preview(
    invite_code: str,
    store: RoomStore = Depends(get_rooms_service),
) -> InviteRoomPreview:
    try:
        room = store.get_room_by_invite_code(invite_code)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found") from exc
    return InviteRoomPreview(
        room_id=room.room_id,
        invite_code=room.invite_code or invite_code,
        status=room.status,
        participant_count=room.participant_count,
        created_at=room.created_at,
        last_activity_at=room.last_activity_at,
        participants=room.participants,
    )


@router.post("/invites/{invite_code}/join", response_model=RoomDetail)
async def join_room_from_invite(
    invite_code: str,
    payload: JoinRoomRequest,
    request: Request,
    store: RoomStore = Depends(get_rooms_service),
    user_store: SQLiteUserStore = Depends(get_user_store),
) -> RoomDetail:
    current_user = user_store.get_user_by_session(request.cookies.get(SESSION_COOKIE_NAME))
    try:
        invited_room = store.get_room_by_invite_code(invite_code)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found") from exc

    resume_participant_id: str | None = None
    if current_user:
        payload = payload.model_copy(update={"icon": current_user.icon})
        try:
            resume_participant_id, _ = user_store.get_room_membership(
                current_user.user_id,
                invited_room.room_id,
            )
        except RoomHistoryNotFoundError:
            resume_participant_id = None
    else:
        payload = payload.model_copy(
            update={
                "display_name": payload.display_name.strip() or "Guest",
                "icon": GUEST_BUNNY_ICON,
            }
        )

    try:
        room = store.join_room(
            invited_room.room_id,
            payload,
            participant_id=resume_participant_id,
            user_id=current_user.user_id if current_user else None,
        )
    except RoomCapacityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room is full") from exc
    if current_user and room.participants:
        participant = (
            next(
                (item for item in room.participants if item.participant_id == resume_participant_id),
                None,
            )
            if resume_participant_id
            else None
        ) or room.participants[-1]
        user_store.record_room_membership(
            current_user.user_id,
            room.room_id,
            participant.participant_id,
        )
        _create_invite_notification_for_joined_user(
            get_settings(),
            user_store,
            current_user.user_id,
            invited_room,
            resume_participant_id,
        )
    return room


@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(
    room_id: str,
    store: RoomStore = Depends(get_rooms_service),
) -> RoomDetail:
    try:
        return store.get_room(room_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc


@router.patch("/{room_id}", response_model=RoomDetail)
async def update_room(
    room_id: str,
    payload: UpdateRoomRequest,
    store: RoomStore = Depends(get_rooms_service),
) -> RoomDetail:
    try:
        return store.update_room(room_id, payload)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc


@router.post("/{room_id}/join", response_model=RoomDetail)
async def join_room(
    room_id: str,
) -> RoomDetail:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail=f"Join by room ID is disabled for {room_id}. Open the private invite link instead.",
    )


@router.delete("/{room_id}/participants/{participant_id}", response_model=RoomDetail)
async def leave_room(
    room_id: str,
    participant_id: str,
    store: RoomStore = Depends(get_rooms_service),
) -> RoomDetail:
    try:
        return store.leave_room(room_id, participant_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room or participant not found") from exc


@router.get("/{room_id}/turns", response_model=list[RoomTurn])
async def list_room_turns(
    room_id: str,
    store: RoomStore = Depends(get_rooms_service),
) -> list[RoomTurn]:
    try:
        return store.list_turns(room_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc


@router.post("/{room_id}/turns/upload", response_model=RoomTurn)
async def upload_room_turn(
    room_id: str,
    participant_id: str = Form(...),
    language: str | None = Form(default=None),
    audio_file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    store: RoomStore = Depends(get_rooms_service),
) -> RoomTurn:
    try:
        participant = store.get_participant(room_id, participant_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room or participant not found") from exc

    audio_bytes = await audio_file.read()
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded audio file is empty")

    try:
        source_text, translations, effective_language = await process_uploaded_audio_turn(
            settings=settings,
            audio_bytes=audio_bytes,
            filename=audio_file.filename,
            content_type=audio_file.content_type,
            source_language=language or participant.language,
        )
    except UploadedAudioProcessingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    turn = store.add_turn(
        room_id=room_id,
        participant=participant,
        source_language=effective_language,
        source_text=source_text,
        translations=translations,
        delivery="upload",
    )
    notification_store = _optional_user_store(settings)
    if notification_store is not None:
        _create_turn_notifications(settings, notification_store, store, room_id, participant, turn)

    live_rooms = get_live_room_manager()
    speaker_payload = {
        "participant_id": participant.participant_id,
        "display_name": participant.display_name,
        "icon": participant.icon,
        "language": participant.language,
    }
    await live_rooms.broadcast(
        room_id,
        {
            "type": "final",
            "payload": {
                "room_id": room_id,
                "speaker": speaker_payload,
                "text": turn.source_text,
                "language": turn.source_language,
                "metrics": {"delivery": "upload"},
            },
        },
    )
    await live_rooms.broadcast(
        room_id,
        {
            "type": "translation",
            "payload": {
                "turn_id": turn.turn_id,
                "room_id": room_id,
                "speaker": speaker_payload,
                "is_final": True,
                "source_language": turn.source_language,
                "source_text": turn.source_text,
                "translations": turn.translations,
                "metrics": {"delivery": "upload"},
            },
        },
    )
    return turn


@router.post("/{room_id}/turns/attachment", response_model=RoomTurn)
async def upload_room_attachment(
    room_id: str,
    participant_id: str = Form(...),
    attachment_file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    store: RoomStore = Depends(get_rooms_service),
) -> RoomTurn:
    try:
        participant = store.get_participant(room_id, participant_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room or participant not found") from exc

    file_bytes = await attachment_file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    original_name = Path(attachment_file.filename or "attachment").name
    suffix = Path(original_name).suffix
    stored_name = f"{secrets.token_hex(12)}{suffix}"
    room_upload_dir = _attachment_upload_dir(settings, room_id)
    file_path = room_upload_dir / stored_name
    file_path.write_bytes(file_bytes)

    attachment = RoomAttachment(
        file_name=original_name,
        file_url=f"/uploads/{room_id}/{stored_name}",
        content_type=attachment_file.content_type or "application/octet-stream",
        size_bytes=len(file_bytes),
    )
    turn = store.add_turn(
        room_id=room_id,
        participant=participant,
        source_language=participant.language,
        source_text=original_name,
        translations={},
        delivery="attachment",
        turn_type="attachment",
        attachment=attachment,
    )
    notification_store = _optional_user_store(settings)
    if notification_store is not None:
        _create_turn_notifications(settings, notification_store, store, room_id, participant, turn)

    live_rooms = get_live_room_manager()
    await live_rooms.broadcast(
        room_id,
        {
            "type": "attachment",
            "payload": turn.model_dump(mode="json"),
        },
    )
    return turn


@router.post("/{room_id}/turns/demo", response_model=RoomTurn)
async def create_demo_room_turn(
    room_id: str,
    payload: CreateDemoTurnRequest,
    settings: Settings = Depends(get_settings),
    store: RoomStore = Depends(get_rooms_service),
) -> RoomTurn:
    try:
        participant = store.get_participant(room_id, payload.participant_id)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room or participant not found") from exc

    try:
        source_text, translations, effective_language = await process_demo_text_turn(
            settings=settings,
            source_text=payload.source_text,
            source_language=payload.language or participant.language,
        )
    except UploadedAudioProcessingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    turn = store.add_turn(
        room_id=room_id,
        participant=participant,
        source_language=effective_language,
        source_text=source_text,
        translations=translations,
        delivery="demo",
    )
    notification_store = _optional_user_store(settings)
    if notification_store is not None:
        _create_turn_notifications(settings, notification_store, store, room_id, participant, turn)

    live_rooms = get_live_room_manager()
    speaker_payload = {
        "participant_id": participant.participant_id,
        "display_name": participant.display_name,
        "icon": participant.icon,
        "language": participant.language,
    }
    await live_rooms.broadcast(
        room_id,
        {
            "type": "final",
            "payload": {
                "room_id": room_id,
                "speaker": speaker_payload,
                "text": turn.source_text,
                "language": turn.source_language,
                "metrics": {"delivery": "demo"},
            },
        },
    )
    await live_rooms.broadcast(
        room_id,
        {
            "type": "translation",
            "payload": {
                "turn_id": turn.turn_id,
                "room_id": room_id,
                "speaker": speaker_payload,
                "is_final": True,
                "source_language": turn.source_language,
                "source_text": turn.source_text,
                "translations": turn.translations,
                "metrics": {"delivery": "demo"},
            },
        },
    )
    return turn
