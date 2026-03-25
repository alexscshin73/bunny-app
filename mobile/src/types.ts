export type SupportedLanguage = "ko" | "es";
export type ConnectionState = "disconnected" | "connecting" | "connected";

export interface RoomParticipant {
  participant_id: string;
  user_id?: string | null;
  display_name: string;
  icon?: string;
  language: SupportedLanguage;
  joined_at: string;
}

export interface RoomDetail {
  room_id: string;
  invite_code?: string | null;
  title?: string;
  status: "waiting" | "ready" | "active" | "ended";
  participant_count: number;
  creator_participant_id?: string | null;
  created_at: string;
  last_activity_at?: string;
  participants: RoomParticipant[];
}

export interface JoinRoomInput {
  displayName: string;
  language: SupportedLanguage;
  inviteCode: string;
}

export interface CreateRoomInput {
  displayName: string;
  language: SupportedLanguage;
  title?: string;
}

export interface InviteRoomPreview {
  room_id: string;
  invite_code: string;
  status: "waiting" | "ready" | "active" | "ended";
  participant_count: number;
  created_at: string;
  last_activity_at: string;
  participants: RoomParticipant[];
}

export interface SpeakerPayload {
  participant_id: string;
  display_name: string;
  language: SupportedLanguage;
}

export interface RoomSocketPayloadBase {
  room_id: string;
  speaker?: SpeakerPayload;
}

export interface RoomReadyEvent {
  type: "room_ready";
  payload: {
    room_id: string;
    participant: SpeakerPayload;
    participants: SpeakerPayload[];
    targets: SupportedLanguage[];
    asr: {
      engine: string;
      ready: boolean;
    };
    translation: {
      engine: string;
      ready: boolean;
    };
  };
}

export interface ParticipantEvent {
  type: "participant_joined" | "participant_left";
  payload: {
    room_id: string;
    participant: SpeakerPayload;
  };
}

export interface SessionStartedEvent {
  type: "session_started";
  payload: RoomSocketPayloadBase & {
    sample_rate: number;
    language: string;
  };
}

export interface ActiveSpeakerState {
  speaker: SpeakerPayload;
  active: boolean;
  language: string;
  sampleRate?: number;
}

export interface SpeakerStateEvent {
  type: "speaker_state";
  payload: RoomSocketPayloadBase & {
    active: boolean;
    language: string;
    sample_rate?: number;
  };
}

export interface PartialOrFinalEvent {
  type: "partial" | "final";
  payload: RoomSocketPayloadBase & {
    text: string;
    language: SupportedLanguage;
    metrics?: Record<string, number>;
  };
}

export interface TranslationEvent {
  type: "translation";
  payload: RoomSocketPayloadBase & {
    turn_id?: string;
    is_final: boolean;
    source_language: SupportedLanguage;
    source_text: string;
    translations: Record<string, string>;
    metrics?: Record<string, number>;
  };
}

export interface StatsEvent {
  type: "stats";
  payload: RoomSocketPayloadBase & Record<string, unknown>;
}

export interface ErrorEvent {
  type: "error";
  payload: {
    message: string;
  };
}

export type RoomSocketEvent =
  | RoomReadyEvent
  | ParticipantEvent
  | SessionStartedEvent
  | SpeakerStateEvent
  | PartialOrFinalEvent
  | TranslationEvent
  | StatsEvent
  | ErrorEvent;

export interface ConversationTurn {
  id: string;
  speaker: SpeakerPayload;
  sourceLanguage: SupportedLanguage;
  sourceText: string;
  translatedText: string;
  isFinal: boolean;
  delivery?: "realtime" | "upload" | "demo" | "system";
  createdAt?: string;
}

export interface ActivityEntry {
  id: string;
  message: string;
}

export interface RoomTurnRecord {
  turn_id: string;
  room_id: string;
  speaker: SpeakerPayload;
  source_language: SupportedLanguage;
  source_text: string;
  translations: Record<string, string>;
  delivery: "realtime" | "upload" | "demo";
  created_at: string;
}

export interface BackendHealth {
  status: string;
  asr: {
    engine: string;
    ready: boolean;
  };
  translation: {
    engine: string;
    ready: boolean;
    targets: string[];
  };
  llm_postedit?: {
    enabled?: boolean;
    ready?: boolean;
    scope?: string;
    history_turns?: number;
    [key: string]: unknown;
  };
  room_store: {
    backend: string;
    max_participants: number;
    ttl_minutes: number;
    cleanup_interval_seconds: number;
  };
}
