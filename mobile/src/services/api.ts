import {
  BackendHealth,
  CreateRoomInput,
  InviteRoomPreview,
  JoinRoomInput,
  RoomDetail,
  RoomTurnRecord,
  SupportedLanguage,
} from "../types";

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.trim().replace(/\/+$/, "");
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      message = `Request failed with ${response.status}`;
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function createRoom(baseUrl: string, input: CreateRoomInput): Promise<RoomDetail> {
  return requestJson<RoomDetail>(`${normalizeBaseUrl(baseUrl)}/api/rooms`, {
    method: "POST",
    body: JSON.stringify({
      display_name: input.displayName.trim(),
      language: input.language,
      title: input.title?.trim() || "",
    }),
  });
}

export async function joinRoom(baseUrl: string, input: JoinRoomInput): Promise<RoomDetail> {
  return requestJson<RoomDetail>(
    `${normalizeBaseUrl(baseUrl)}/api/rooms/invites/${input.inviteCode.trim()}/join`,
    {
      method: "POST",
      body: JSON.stringify({
        display_name: input.displayName.trim(),
        language: input.language,
      }),
    }
  );
}

export async function fetchInvitePreview(
  baseUrl: string,
  inviteCode: string
): Promise<InviteRoomPreview> {
  return requestJson<InviteRoomPreview>(
    `${normalizeBaseUrl(baseUrl)}/api/rooms/invites/${inviteCode.trim()}`
  );
}

export async function createDemoTurn(
  baseUrl: string,
  roomId: string,
  participantId: string,
  language: SupportedLanguage,
  sourceText: string
): Promise<RoomTurnRecord> {
  return requestJson<RoomTurnRecord>(`${normalizeBaseUrl(baseUrl)}/api/rooms/${roomId}/turns/demo`, {
    method: "POST",
    body: JSON.stringify({
      participant_id: participantId,
      language,
      source_text: sourceText,
    }),
  });
}

function inferMimeTypeFromUri(uri: string): string {
  const normalized = uri.toLowerCase();
  if (normalized.endsWith(".wav")) {
    return "audio/wav";
  }
  if (normalized.endsWith(".m4a")) {
    return "audio/x-m4a";
  }
  if (normalized.endsWith(".webm")) {
    return "audio/webm";
  }
  return "application/octet-stream";
}

export async function uploadRecordedTurn(
  baseUrl: string,
  roomId: string,
  participantId: string,
  language: SupportedLanguage,
  fileUri: string
): Promise<RoomTurnRecord> {
  const form = new FormData();
  form.append("participant_id", participantId);
  form.append("language", language);
  form.append("audio_file", {
    uri: fileUri,
    name: fileUri.split("/").pop() || "turn.m4a",
    type: inferMimeTypeFromUri(fileUri),
  } as never);

  const response = await fetch(`${normalizeBaseUrl(baseUrl)}/api/rooms/${roomId}/turns/upload`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let message = "Audio upload failed";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      message = `Audio upload failed with ${response.status}`;
    }
    throw new Error(message);
  }

  return (await response.json()) as RoomTurnRecord;
}

export async function fetchRoomTurns(baseUrl: string, roomId: string): Promise<RoomTurnRecord[]> {
  return requestJson<RoomTurnRecord[]>(`${normalizeBaseUrl(baseUrl)}/api/rooms/${roomId}/turns`);
}

export async function updateRoomTitle(
  baseUrl: string,
  roomId: string,
  title: string
): Promise<RoomDetail> {
  return requestJson<RoomDetail>(`${normalizeBaseUrl(baseUrl)}/api/rooms/${roomId}`, {
    method: "PATCH",
    body: JSON.stringify({
      title: title.trim(),
    }),
  });
}

export async function fetchBackendHealth(baseUrl: string): Promise<BackendHealth> {
  return requestJson<BackendHealth>(`${normalizeBaseUrl(baseUrl)}/healthz`);
}
