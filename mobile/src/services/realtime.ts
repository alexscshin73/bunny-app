function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.trim().replace(/\/+$/, "");
}

export function roomSocketUrl(baseUrl: string, roomId: string, participantId: string): string {
  const normalized = normalizeBaseUrl(baseUrl);

  if (normalized.startsWith("https://")) {
    return `${normalized.replace(/^https/, "wss")}/ws/rooms/${roomId}?participant_id=${participantId}`;
  }

  if (normalized.startsWith("http://")) {
    return `${normalized.replace(/^http/, "ws")}/ws/rooms/${roomId}?participant_id=${participantId}`;
  }

  if (normalized.startsWith("wss://") || normalized.startsWith("ws://")) {
    return `${normalized}/ws/rooms/${roomId}?participant_id=${participantId}`;
  }

  return `ws://${normalized}/ws/rooms/${roomId}?participant_id=${participantId}`;
}
