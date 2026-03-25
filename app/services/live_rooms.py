from dataclasses import dataclass
from functools import lru_cache

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.models.rooms import RoomParticipant
from app.services.session import RealtimeSession


class ParticipantAlreadyConnectedError(ValueError):
    pass


@dataclass
class LiveConnection:
    websocket: WebSocket
    participant: RoomParticipant
    session: RealtimeSession


class LiveRoomManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, LiveConnection]] = {}

    async def connect(
        self,
        room_id: str,
        participant: RoomParticipant,
        websocket: WebSocket,
        session: RealtimeSession,
    ) -> None:
        room_connections = self._rooms.setdefault(room_id, {})
        existing = room_connections.get(participant.participant_id)
        if existing is not None and existing.websocket is not websocket:
            await self.send_json(
                existing.websocket,
                {
                    "type": "error",
                    "payload": {
                        "message": "This account reconnected from another device.",
                    },
                },
            )
            if existing.websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await existing.websocket.close(code=4409)
                except RuntimeError:
                    pass
        room_connections[participant.participant_id] = LiveConnection(
            websocket=websocket,
            participant=participant,
            session=session,
        )

    def disconnect(
        self,
        room_id: str,
        participant_id: str,
        websocket: WebSocket | None = None,
    ) -> None:
        room_connections = self._rooms.get(room_id)
        if not room_connections:
            return
        existing = room_connections.get(participant_id)
        if existing is None:
            return
        if websocket is not None and existing.websocket is not websocket:
            return
        room_connections.pop(participant_id, None)
        if not room_connections:
            self._rooms.pop(room_id, None)

    async def send_json(self, websocket: WebSocket, message: dict[str, object]) -> None:
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        try:
            await websocket.send_json(message)
        except RuntimeError:
            return

    async def broadcast(
        self,
        room_id: str,
        message: dict[str, object],
        exclude_participant_ids: set[str] | None = None,
    ) -> None:
        room_connections = self._rooms.get(room_id, {})
        excluded = exclude_participant_ids or set()
        for participant_id, connection in room_connections.items():
            if participant_id in excluded:
                continue
            await self.send_json(connection.websocket, message)


@lru_cache
def get_live_room_manager() -> LiveRoomManager:
    return LiveRoomManager()
