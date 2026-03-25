import AsyncStorage from "@react-native-async-storage/async-storage";
import { startTransition, useEffect, useRef, useState } from "react";

import { DEFAULT_BACKEND_URL } from "../config";
import {
  createDemoTurn,
  createRoom,
  fetchBackendHealth,
  fetchRoomTurns,
  joinRoom,
  updateRoomTitle,
  uploadRecordedTurn,
} from "../services/api";
import { roomSocketUrl } from "../services/realtime";
import {
  ActiveSpeakerState,
  ActivityEntry,
  BackendHealth,
  ConnectionState,
  ConversationTurn,
  CreateRoomInput,
  JoinRoomInput,
  RoomDetail,
  RoomParticipant,
  RoomSocketEvent,
  SpeakerPayload,
} from "../types";

type LiveTurnMap = Record<string, ConversationTurn>;
const BACKEND_URL_STORAGE_KEY = "bunny.backend_url";
const ROOM_TITLE_SEQUENCE_STORAGE_KEY = "bunny.room_title_sequence";
const DEMO_SEQUENCE_LINES = {
  ko: "안녕하세요, 오늘 한국 팀과 멕시코 팀의 실시간 통역 데모를 시작하겠습니다.",
  es: "Hola, hoy vamos a empezar la demo de interpretacion en tiempo real entre Mexico y Corea.",
  koFollowup: "이 흐름은 자막, 히스토리, 그리고 음성 재생까지 한 번에 확인하는 용도입니다.",
};

function makeId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function normalizeBackendUrl(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return DEFAULT_BACKEND_URL;
  }
  return trimmed.replace(/\/+$/, "");
}

function upsertParticipant(participants: RoomParticipant[], participant: SpeakerPayload): RoomParticipant[] {
  const next = participants.filter((item) => item.participant_id !== participant.participant_id);
  next.push({
    participant_id: participant.participant_id,
    display_name: participant.display_name,
    language: participant.language,
    joined_at: new Date().toISOString(),
  });
  return next;
}

function removeParticipant(participants: RoomParticipant[], participantId: string): RoomParticipant[] {
  return participants.filter((item) => item.participant_id !== participantId);
}

function participantsFromSpeakers(participants: SpeakerPayload[]): RoomParticipant[] {
  return participants.map((participant) => ({
    participant_id: participant.participant_id,
    display_name: participant.display_name,
    language: participant.language,
    joined_at: new Date().toISOString(),
  }));
}

function buildActivity(message: string): ActivityEntry {
  return {
    id: makeId("activity"),
    message,
  };
}

function buildSystemTurn(message: string, participant: SpeakerPayload): ConversationTurn {
  return {
    id: makeId("system"),
    speaker: participant,
    sourceLanguage: participant.language,
    sourceText: message,
    translatedText: "",
    isFinal: true,
    delivery: "system",
    createdAt: new Date().toISOString(),
  };
}

function baseRoomTitle(displayName: string | null | undefined): string {
  const ownerName = String(displayName || "").trim() || "User";
  return `${ownerName}'s Room`;
}

function fallbackRoomTitle(displayName: string | null | undefined): string {
  return baseRoomTitle(displayName);
}

async function readRoomTitleSequenceMap(): Promise<Record<string, number>> {
  try {
    const raw = await AsyncStorage.getItem(ROOM_TITLE_SEQUENCE_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw) as Record<string, number> | null;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

async function nextAutoRoomTitle(displayName: string | null | undefined): Promise<string> {
  const ownerName = String(displayName || "").trim() || "User";
  const sequenceMap = await readRoomTitleSequenceMap();
  const currentSequence = Number.isFinite(sequenceMap[ownerName]) ? sequenceMap[ownerName] : 0;
  const nextSequence = currentSequence + 1;
  sequenceMap[ownerName] = nextSequence;
  try {
    await AsyncStorage.setItem(ROOM_TITLE_SEQUENCE_STORAGE_KEY, JSON.stringify(sequenceMap));
  } catch {
    // Ignore persistence failures and keep the generated title for this request.
  }
  return `${baseRoomTitle(displayName)} ${String(nextSequence).padStart(2, "0")}`;
}

function isNonverbalText(text: string): boolean {
  const stripped = text.trim();
  if (!stripped) {
    return false;
  }
  const hasWordLike = Array.from(stripped).some((char) => {
    if (/[0-9A-Za-z]/.test(char) || /[가-힣]/.test(char)) {
      return true;
    }
    return char.toLowerCase() !== char.toUpperCase();
  });
  if (hasWordLike) {
    return false;
  }
  return Array.from(stripped).some((char) => !/\s/.test(char));
}

function turnFromRecord(
  turn: {
    turn_id: string;
    speaker: SpeakerPayload;
    source_language: SpeakerPayload["language"];
    source_text: string;
    translations: Record<string, string>;
    delivery: "realtime" | "upload" | "demo";
    created_at: string;
  },
  viewerLanguage: SpeakerPayload["language"]
): ConversationTurn {
  const translatedText =
    turn.translations[viewerLanguage] ?? turn.translations[turn.source_language] ?? "";
  return {
    id: turn.turn_id,
    speaker: turn.speaker,
    sourceLanguage: turn.source_language,
    sourceText: turn.source_text,
    translatedText: !translatedText && isNonverbalText(turn.source_text) ? "" : translatedText,
    isFinal: true,
    delivery: turn.delivery,
    createdAt: turn.created_at,
  };
}

export function useRoomSession() {
  const [backendUrl, setBackendUrl] = useState(DEFAULT_BACKEND_URL);
  const [room, setRoom] = useState<RoomDetail | null>(null);
  const [selfParticipant, setSelfParticipant] = useState<RoomParticipant | null>(null);
  const [activeTurnParticipantId, setActiveTurnParticipantId] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [liveTurns, setLiveTurns] = useState<LiveTurnMap>({});
  const [activityFeed, setActivityFeed] = useState<ActivityEntry[]>([]);
  const [lastStats, setLastStats] = useState<Record<string, unknown> | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRunningDemoSequence, setIsRunningDemoSequence] = useState(false);
  const [isRefreshingHistory, setIsRefreshingHistory] = useState(false);
  const [latestDeliveredTurn, setLatestDeliveredTurn] = useState<ConversationTurn | null>(null);
  const [activeSpeakerState, setActiveSpeakerState] = useState<ActiveSpeakerState | null>(null);
  const [backendHealth, setBackendHealth] = useState<BackendHealth | null>(null);
  const [isCheckingBackendHealth, setIsCheckingBackendHealth] = useState(false);
  const [backendHealthError, setBackendHealthError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const hasLoadedBackendUrl = useRef(false);

  function pushActivity(message: string) {
    startTransition(() => {
      setActivityFeed((current) => [buildActivity(message), ...current].slice(0, 12));
    });
  }

  function resetConversationState() {
    setTurns([]);
    setLiveTurns({});
    setLastStats(null);
    setActivityFeed([]);
    setLatestDeliveredTurn(null);
    setActiveSpeakerState(null);
    setActiveTurnParticipantId(null);
  }

  function closeSocket() {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    setActiveSpeakerState(null);
    setConnectionState("disconnected");
  }

  function updateBackendUrl(value: string) {
    setBackendUrl(normalizeBackendUrl(value));
  }

  async function refreshBackendHealth(urlOverride?: string) {
    const nextUrl = normalizeBackendUrl(urlOverride ?? backendUrl);
    setIsCheckingBackendHealth(true);
    setBackendHealthError(null);
    try {
      const health = await fetchBackendHealth(nextUrl);
      setBackendHealth(health);
      return health;
    } catch (error) {
      setBackendHealth(null);
      setBackendHealthError(
        error instanceof Error ? error.message : "Failed to connect to the backend health endpoint."
      );
      return null;
    } finally {
      setIsCheckingBackendHealth(false);
    }
  }

  function attachSocket(nextRoom: RoomDetail, participant: RoomParticipant) {
    closeSocket();
    setConnectionState("connecting");

    const socket = new WebSocket(roomSocketUrl(backendUrl, nextRoom.room_id, participant.participant_id));
    socketRef.current = socket;

    socket.onopen = () => {
      setConnectionState("connected");
      pushActivity(`Connected to room ${nextRoom.room_id}.`);
    };

    socket.onmessage = (message) => {
      const event = JSON.parse(message.data) as RoomSocketEvent;
      handleSocketEvent(event);
    };

    socket.onerror = () => {
      setErrorMessage("Realtime connection failed.");
      pushActivity("Realtime connection reported an error.");
    };

    socket.onclose = () => {
      socketRef.current = null;
      setActiveSpeakerState(null);
      setConnectionState("disconnected");
      pushActivity("Realtime connection closed.");
    };
  }

  function promoteLiveTurn(turn: ConversationTurn) {
    startTransition(() => {
      setTurns((current) => {
        const filtered = current.filter((item) => item.id !== turn.id);
        return [...filtered, turn].slice(-40);
      });
      if (turn.delivery !== "system") {
        setLatestDeliveredTurn(turn);
      }
    });
  }

  async function refreshRoomHistory(nextRoom: RoomDetail, participant: RoomParticipant) {
    setIsRefreshingHistory(true);
    try {
      const records = await fetchRoomTurns(backendUrl, nextRoom.room_id);
      setTurns(records.map((turn) => turnFromRecord(turn, participant.language)).slice(-40));
    } catch (error) {
      pushActivity(error instanceof Error ? error.message : "Failed to refresh room history.");
    } finally {
      setIsRefreshingHistory(false);
    }
  }

  function handleSocketEvent(event: RoomSocketEvent) {
    if (event.type === "room_ready") {
      pushActivity(`Room ${event.payload.room_id} is ready for ${event.payload.participant.display_name}.`);
      setRoom((current) => {
        if (!current) {
          return current;
        }
        return {
          ...current,
          participants: participantsFromSpeakers(event.payload.participants),
          participant_count: event.payload.participants.length,
          status: event.payload.participants.length >= 2 ? "ready" : "waiting",
        };
      });
      return;
    }

    if (event.type === "participant_joined") {
      setRoom((current) => {
        if (!current) {
          return current;
        }
        const participants = upsertParticipant(current.participants, event.payload.participant);
        return { ...current, participants, participant_count: participants.length, status: "ready" };
      });
      pushActivity(`${event.payload.participant.display_name} joined the room.`);
      promoteLiveTurn(buildSystemTurn(`${event.payload.participant.display_name}님이 입장했습니다.`, event.payload.participant));
      return;
    }

    if (event.type === "participant_left") {
      setRoom((current) => {
        if (!current) {
          return current;
        }
        const participants = removeParticipant(current.participants, event.payload.participant.participant_id);
        return {
          ...current,
          participants,
          participant_count: participants.length,
          status: participants.length >= 2 ? "ready" : "waiting",
        };
      });
      pushActivity(`${event.payload.participant.display_name} left the room.`);
      promoteLiveTurn(buildSystemTurn(`${event.payload.participant.display_name}님이 퇴장했습니다.`, event.payload.participant));
      return;
    }

    if (event.type === "session_started") {
      if (event.payload.speaker) {
        pushActivity(`${event.payload.speaker.display_name} started a live speaking session.`);
      }
      return;
    }

    if (event.type === "speaker_state") {
      const speaker = event.payload.speaker;
      if (!speaker) {
        setActiveSpeakerState(null);
        return;
      }

      if (event.payload.active) {
        setActiveSpeakerState({
          speaker,
          active: true,
          language: event.payload.language,
          sampleRate: event.payload.sample_rate,
        });
        setActiveTurnParticipantId(speaker.participant_id);
        pushActivity(`${speaker.display_name} is speaking live now.`);
        return;
      }

      setActiveSpeakerState((current) =>
        current?.speaker.participant_id === speaker.participant_id ? null : current
      );
      pushActivity(`${speaker.display_name} finished the live turn.`);
      return;
    }

    if (event.type === "partial" || event.type === "final") {
      const speaker = event.payload.speaker;
      if (!speaker) {
        return;
      }

      setLiveTurns((current) => ({
        ...current,
        [speaker.participant_id]: {
          id: current[speaker.participant_id]?.id ?? makeId("turn"),
          speaker,
          sourceLanguage: event.payload.language,
          sourceText: event.payload.text,
          translatedText: current[speaker.participant_id]?.translatedText ?? "",
          isFinal: event.type === "final",
        },
      }));
      return;
    }

    if (event.type === "translation") {
      const speaker = event.payload.speaker;
      if (!speaker) {
        return;
      }

      const translatedText =
        event.payload.translations[selfParticipant?.language ?? speaker.language] ??
        event.payload.translations[speaker.language] ??
        "";
      const effectiveTranslatedText =
        !translatedText && isNonverbalText(event.payload.source_text) ? "" : translatedText;

      let finalizedTurn: ConversationTurn | null = null;
      setLiveTurns((current) => {
        const nextTurn: ConversationTurn = {
          id: event.payload.turn_id ?? current[speaker.participant_id]?.id ?? makeId("turn"),
          speaker,
          sourceLanguage: event.payload.source_language,
          sourceText: event.payload.source_text,
          translatedText: effectiveTranslatedText,
          isFinal: event.payload.is_final,
          delivery: "realtime",
          createdAt: new Date().toISOString(),
        };

        if (event.payload.is_final) {
          finalizedTurn = nextTurn;
          const { [speaker.participant_id]: _removed, ...rest } = current;
          return rest;
        }

        return {
          ...current,
          [speaker.participant_id]: nextTurn,
        };
      });
      if (finalizedTurn) {
        promoteLiveTurn(finalizedTurn);
      }
      return;
    }

    if (event.type === "stats") {
      setLastStats(event.payload);
      let finalizedTurns: ConversationTurn[] = [];
      setLiveTurns((current) => {
        finalizedTurns = Object.values(current).filter((turn) => turn.isFinal);
        const pending = Object.fromEntries(
          Object.entries(current).filter(([, turn]) => !turn.isFinal)
        ) as LiveTurnMap;
        return pending;
      });
      if (finalizedTurns.length > 0) {
        finalizedTurns.forEach(promoteLiveTurn);
      }
      return;
    }

    if (event.type === "error") {
      setErrorMessage(event.payload.message);
      pushActivity(event.payload.message);
    }
  }

  async function createRoomAction(input: CreateRoomInput) {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const requestedTitle = input.title?.trim() || "";
      const nextRoom = await createRoom(backendUrl, {
        ...input,
        title: requestedTitle || (await nextAutoRoomTitle(input.displayName)),
      });
      const participant = nextRoom.participants[0];
      resetConversationState();
      setRoom(nextRoom);
      setSelfParticipant(participant);
      setActiveTurnParticipantId(participant.participant_id);
      await refreshRoomHistory(nextRoom, participant);
      attachSocket(nextRoom, participant);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create room.";
      setErrorMessage(
        message === "Sign in to create a room."
          ? "Creating a new room now requires a signed-in account on the current backend. Join from a private invite on mobile, or create the room from the web app first."
          : message
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function joinRoomAction(input: JoinRoomInput) {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const nextRoom = await joinRoom(backendUrl, input);
      const participant = nextRoom.participants[nextRoom.participants.length - 1];
      resetConversationState();
      setRoom(nextRoom);
      setSelfParticipant(participant);
      setActiveTurnParticipantId(participant.participant_id);
      await refreshRoomHistory(nextRoom, participant);
      attachSocket(nextRoom, participant);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to join room.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function addDemoGuest() {
    if (!room || !selfParticipant) {
      throw new Error("Create or join a room before adding a demo guest.");
    }
    await ensureDemoGuest();
  }

  async function ensureDemoGuest() {
    if (!room || !selfParticipant) {
      throw new Error("Create or join a room before adding a demo guest.");
    }
    if (room.participants.length >= 2) {
      pushActivity("This room already has two participants.");
      return room;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const guestLanguage = selfParticipant.language === "ko" ? "es" : "ko";
      const guestName = guestLanguage === "ko" ? "Minji Demo" : "Luis Demo";
      const nextRoom = await joinRoom(backendUrl, {
        displayName: guestName,
        language: guestLanguage,
        inviteCode: room.invite_code || room.room_id,
      });
      setRoom(nextRoom);
      pushActivity(`${guestName} joined as a demo guest.`);
      return nextRoom;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to add demo guest.";
      setErrorMessage(message);
      throw new Error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function startSession(sampleRate: number, language: SpeakerPayload["language"]) {
    if (!socketRef.current) {
      return;
    }
    socketRef.current.send(
      JSON.stringify({
        type: "start",
        sample_rate: sampleRate,
        language,
      })
    );
  }

  function stopSession() {
    if (!socketRef.current) {
      return;
    }
    socketRef.current.send(JSON.stringify({ type: "stop" }));
  }

  function ping() {
    if (!socketRef.current) {
      return;
    }
    socketRef.current.send(JSON.stringify({ type: "ping" }));
  }

  function sendAudioChunk(chunk: ArrayBuffer) {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return false;
    }
    socketRef.current.send(chunk);
    return true;
  }

  function leaveRoom() {
    closeSocket();
    setRoom(null);
    setSelfParticipant(null);
    resetConversationState();
    setErrorMessage(null);
  }

  function goHome() {
    leaveRoom();
  }

  function cycleSelfLanguage() {
    setSelfParticipant((current) => {
      if (!current) {
        return current;
      }
      const nextLanguage = current.language === "ko" ? "es" : "ko";
      setRoom((activeRoom) => {
        if (!activeRoom) {
          return activeRoom;
        }
        return {
          ...activeRoom,
          participants: activeRoom.participants.map((participant) =>
            participant.participant_id === current.participant_id
              ? { ...participant, language: nextLanguage }
              : participant
          ),
        };
      });
      setActiveSpeakerState((activeState) =>
        activeState?.speaker.participant_id === current.participant_id
          ? {
              ...activeState,
              language: nextLanguage,
              speaker: { ...activeState.speaker, language: nextLanguage },
            }
          : activeState
      );
      pushActivity(`${current.display_name} language changed to ${nextLanguage.toUpperCase()}.`);
      return { ...current, language: nextLanguage };
    });
  }

  async function saveRoomTitle(title: string) {
    if (!room) {
      throw new Error("Create or join a room before editing the title.");
    }

    const nextTitle = title.trim();
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const updatedRoom = await updateRoomTitle(backendUrl, room.room_id, nextTitle);
      setRoom(updatedRoom);
      pushActivity(`Room title updated to ${nextTitle || fallbackRoomTitle(selfParticipant?.display_name)}.`);
      return updatedRoom;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to update the room title.";
      setErrorMessage(message);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function uploadNativeRecording(fileUri: string) {
    if (!room || !selfParticipant) {
      throw new Error("Join a room before uploading recorded audio.");
    }

    const activeSpeaker =
      room.participants.find((participant) => participant.participant_id === activeTurnParticipantId) ??
      selfParticipant;

    const turn = await uploadRecordedTurn(
      backendUrl,
      room.room_id,
      activeSpeaker.participant_id,
      activeSpeaker.language,
      fileUri
    );

    pushActivity(`${activeSpeaker.display_name} uploaded a recorded turn.`);
    await refreshRoomHistory(room, selfParticipant);
    if (connectionState !== "connected") {
      promoteLiveTurn(turnFromRecord(turn, selfParticipant.language));
    }
    return turn;
  }

  async function sendDemoTurn(participantId: string, sourceText: string) {
    if (!room || !selfParticipant) {
      throw new Error("Join a room before sending a demo turn.");
    }

    const speaker =
      room.participants.find((participant) => participant.participant_id === participantId) ?? null;
    if (!speaker) {
      throw new Error("Selected demo speaker is not in this room.");
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const turn = await createDemoTurn(
        backendUrl,
        room.room_id,
        speaker.participant_id,
        speaker.language,
        sourceText
      );
      pushActivity(`${speaker.display_name} sent a demo turn.`);
      await refreshRoomHistory(room, selfParticipant);
      if (connectionState !== "connected") {
        promoteLiveTurn(turnFromRecord(turn, selfParticipant.language));
      }
      return turn;
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to send demo turn.");
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function runDemoSequence() {
    if (!room || !selfParticipant) {
      throw new Error("Join a room before running the demo sequence.");
    }

    setIsRunningDemoSequence(true);
    setErrorMessage(null);
    try {
      const activeRoom = await ensureDemoGuest();
      const koreanSpeaker =
        activeRoom.participants.find((participant) => participant.language === "ko") ?? selfParticipant;
      const spanishSpeaker =
        activeRoom.participants.find((participant) => participant.language === "es") ?? selfParticipant;

      await sendDemoTurn(koreanSpeaker.participant_id, DEMO_SEQUENCE_LINES.ko);
      await delay(350);
      await sendDemoTurn(spanishSpeaker.participant_id, DEMO_SEQUENCE_LINES.es);
      await delay(350);
      await sendDemoTurn(koreanSpeaker.participant_id, DEMO_SEQUENCE_LINES.koFollowup);
      pushActivity("Demo sequence completed.");
    } finally {
      setIsRunningDemoSequence(false);
    }
  }

  useEffect(() => {
    AsyncStorage.getItem(BACKEND_URL_STORAGE_KEY)
      .then((storedValue) => {
        if (storedValue) {
          setBackendUrl(normalizeBackendUrl(storedValue));
        }
      })
      .finally(() => {
        hasLoadedBackendUrl.current = true;
      });
  }, []);

  useEffect(() => {
    if (!hasLoadedBackendUrl.current) {
      return;
    }

    AsyncStorage.setItem(BACKEND_URL_STORAGE_KEY, backendUrl).catch(() => {});
  }, [backendUrl]);

  useEffect(() => {
    const handle = setTimeout(() => {
      refreshBackendHealth(backendUrl).catch(() => {});
    }, 350);

    return () => clearTimeout(handle);
  }, [backendUrl]);

  useEffect(() => {
    if (!room || room.participants.length === 0) {
      return;
    }

    if (!room.participants.some((participant) => participant.participant_id === activeTurnParticipantId)) {
      setActiveTurnParticipantId(room.participants[0]?.participant_id ?? null);
    }
  }, [activeTurnParticipantId, room]);

  useEffect(() => {
    if (!room || !selfParticipant) {
      return;
    }

    const interval = setInterval(() => {
      refreshRoomHistory(room, selfParticipant).catch(() => {});
    }, 15000);

    return () => clearInterval(interval);
  }, [backendUrl, room, selfParticipant]);

  useEffect(() => {
    return () => {
      closeSocket();
    };
  }, []);

  return {
    activeTurnParticipant:
      room?.participants.find((participant) => participant.participant_id === activeTurnParticipantId) ??
      selfParticipant,
    activeSpeakerState,
    activityFeed,
    backendHealth,
    backendHealthError,
    backendUrl,
    connectionState,
    createRoom: createRoomAction,
    errorMessage,
    isCheckingBackendHealth,
    isRunningDemoSequence,
    isSubmitting,
    joinRoom: joinRoomAction,
    lastStats,
    leaveRoom,
    liveTurns,
    goHome,
    ping,
    room,
    saveRoomTitle,
    sendAudioChunk,
    selfParticipant,
    cycleSelfLanguage,
    setBackendUrl: updateBackendUrl,
    setActiveTurnParticipant: setActiveTurnParticipantId,
    startSession,
    stopSession,
    turns,
    uploadNativeRecording,
    refreshBackendHealth: () => refreshBackendHealth(),
    refreshRoomHistory: room && selfParticipant ? () => refreshRoomHistory(room, selfParticipant) : undefined,
    addDemoGuest,
    runDemoSequence,
    sendDemoTurn,
    isRefreshingHistory,
    latestDeliveredTurn,
  };
}

function delay(milliseconds: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}
