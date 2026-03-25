const displayNameInput = document.getElementById("displayNameInput");
const languageSelect = document.getElementById("languageSelect");
const profileNotificationSelect = document.getElementById("profileNotificationSelect");
const profileBioInput = document.getElementById("profileBioInput");
const roomCodeInput = document.getElementById("roomCodeInput");
const authScreenEl = document.getElementById("authScreen");
const serviceScreenEl = document.getElementById("serviceScreen");
const serviceHeaderShellEl = document.getElementById("serviceHeaderShell");
const serviceMainShellEl = document.getElementById("serviceMainShell");
const chatScreenShellEl = document.getElementById("chatScreenShell");
const setupStatusEl = document.getElementById("setupStatus");
const authGuestShellEl = document.getElementById("authGuestShell");
const guestInviteCardEl = document.getElementById("guestInviteCard");
const guestInviteRoomEl = document.getElementById("guestInviteRoom");
const continueGuestButton = document.getElementById("continueGuestButton");
const accountSessionShellEl = document.getElementById("accountSessionShell");
const accountStatusEl = document.getElementById("accountStatus");
const authHeroTitleEl = document.getElementById("authHeroTitle");
const authHeroCopyEl = document.getElementById("authHeroCopy");
const registerForm = document.getElementById("registerForm");
const registerNameInput = document.getElementById("registerNameInput");
const registerPhoneInput = document.getElementById("registerPhoneInput");
const registerCountryCodeSelect = document.getElementById("registerCountryCodeSelect");
const registerAvatarInput = document.getElementById("registerAvatarInput");
const registerPasswordInput = document.getElementById("registerPasswordInput");
const registerPasswordConfirmInput = document.getElementById("registerPasswordConfirmInput");
const registerAvatarGridEl = document.getElementById("registerAvatarGrid");
const avatarLibraryCountEl = document.getElementById("avatarLibraryCount");
const loginForm = document.getElementById("loginForm");
const loginCountryCodeSelect = document.getElementById("loginCountryCodeSelect");
const loginPhoneInput = document.getElementById("loginPhoneInput");
const loginPasswordInput = document.getElementById("loginPasswordInput");
const showRegisterButton = document.getElementById("showRegisterButton");
const showLoginButton = document.getElementById("showLoginButton");
const logoutButton = document.getElementById("logoutButton");
const notificationsButton = document.getElementById("notificationsButton");
const openMyPageButton = document.getElementById("openMyPageButton");
const editProfileButton = document.getElementById("editProfileButton");
const closeMyPageButton = document.getElementById("closeMyPageButton");
const sessionAvatarEl = document.getElementById("sessionAvatar");
const sessionNameEl = document.getElementById("sessionName");
const sessionPhoneEl = document.getElementById("sessionPhone");
const sessionHomeNoticeEl = document.getElementById("sessionHomeNotice");
const sessionBioEl = document.getElementById("sessionBio");
const saveProfileButton = document.getElementById("saveProfileButton");
const profileAvatarPreviewEl = document.getElementById("profileAvatarPreview");
const profilePhoneTextEl = document.getElementById("profilePhoneText");
const profileBioPreviewEl = document.getElementById("profileBioPreview");
const profileAvatarGridEl = document.getElementById("profileAvatarGrid");
const profileAvatarInput = document.getElementById("profileAvatarInput");
const profileAvatarCountEl = document.getElementById("profileAvatarCount");
const mypageShellEl = document.getElementById("mypageShell");
const notificationsShellEl = document.getElementById("notificationsShell");
const notificationListEl = document.getElementById("notificationList");
const notificationUnreadBadgeEl = document.getElementById("notificationUnreadBadge");
const webPushStatusEl = document.getElementById("webPushStatus");
const webPushToggleButton = document.getElementById("webPushToggleButton");
const markAllNotificationsReadButton = document.getElementById("markAllNotificationsReadButton");
const createHistoryButton = document.getElementById("createHistoryButton");
const joinHistoryButton = document.getElementById("joinHistoryButton");
const downloadHistoryButton = document.getElementById("downloadHistoryButton");
const deleteHistoryButton = document.getElementById("deleteHistoryButton");
const historyListEl = document.getElementById("historyList");
const historyDetailEl = document.getElementById("historyDetail");
const joinRoomButton = document.getElementById("joinRoomButton");
const copyInviteButton = document.getElementById("copyInviteButton");
const emailInviteButton = document.getElementById("emailInviteButton");
const smsInviteButton = document.getElementById("smsInviteButton");
const shareInviteButton = document.getElementById("shareInviteButton");
const invitePreviewEl = document.getElementById("invitePreview");
const invitePreviewBadgeEl = document.getElementById("invitePreviewBadge");
const invitePreviewTitleEl = document.getElementById("invitePreviewTitle");
const invitePreviewBodyEl = document.getElementById("invitePreviewBody");
const asrReadinessEl = document.getElementById("asrReadiness");
const translationReadinessEl = document.getElementById("translationReadiness");
const browserReadinessEl = document.getElementById("browserReadiness");
const demoReadinessEl = document.getElementById("demoReadiness");
const roomTitleEl = document.getElementById("roomTitle");
const socketStatusEl = document.getElementById("socketStatus");
const metricsEl = document.getElementById("metrics");
const micStatusEl = document.getElementById("micStatus");
const participantListEl = document.getElementById("participantList");
const chatRoomTitleInput = document.getElementById("chatRoomTitleInput");
const chatRoomTitleDisplay = document.getElementById("chatRoomTitleDisplay");
const chatRoomTitleText = document.getElementById("chatRoomTitleText");
const chatRoomTitleEditButton = document.getElementById("chatRoomTitleEditButton");
const chatLanguageSelect = document.getElementById("chatLanguageSelect");
const chatInviteButton = document.getElementById("chatInviteButton");
const inviteCardEl = document.getElementById("inviteCard");
const inviteCardTitleEl = document.getElementById("inviteCardTitle");
const inviteCardBodyEl = document.getElementById("inviteCardBody");
const inviteRoomCodeButton = document.getElementById("inviteRoomCodeButton");
const inviteLinkAnchorEl = document.getElementById("inviteLinkAnchor");
const appLinkAnchorEl = document.getElementById("appLinkAnchor");
const shareAppButton = document.getElementById("shareAppButton");
const hostStatusDotEl = document.getElementById("hostStatusDot");
const hostStatusTextEl = document.getElementById("hostStatusText");
const conversationEl = document.getElementById("conversation");
const emptyStateEl = document.getElementById("emptyState");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const homeRoomButton = document.getElementById("homeRoomButton");
const exitRoomButton = document.getElementById("exitRoomButton");
const textShellEl = document.getElementById("textShell");
const textShellTitleEl = document.getElementById("textShellTitle");
const textStatusEl = document.getElementById("textStatus");
const attachmentInput = document.getElementById("attachmentInput");
const textTurnInput = document.getElementById("textTurnInput");
const sendAttachmentButton = document.getElementById("sendAttachmentButton");
const sendTextTurnButton = document.getElementById("sendTextTurnButton");
const emojiPickerButton = document.getElementById("emojiPickerButton");
const emojiPickerPanel = document.getElementById("emojiPickerPanel");
const emojiPickerGrid = document.getElementById("emojiPickerGrid");
const turnGuideTitleEl = document.getElementById("turnGuideTitle");
const turnGuideBodyEl = document.getElementById("turnGuideBody");
const liveCaptionEl = document.getElementById("liveCaption");
const liveCaptionMetaEl = document.getElementById("liveCaptionMeta");
const liveSourceTextEl = document.getElementById("liveSourceText");
const liveTranslatedTextEl = document.getElementById("liveTranslatedText");

const MAX_CONVERSATION_TURNS = 60;
const MAX_SOCKET_BUFFERED_BYTES = 512 * 1024;
const PING_INTERVAL_MS = 10000;
const RUNTIME_POLL_INTERVAL_MS = 30000;
const HISTORY_POLL_INTERVAL_MS = 12000;
const STORAGE_KEY = "bunny-room-web-client";
const ROOM_ID_SEQUENCE_KEY = "bunny-room-id-sequence";
const DEFAULT_CREATE_LANGUAGE = "";
const DEFAULT_AVATAR_ID = "";
const GUEST_ICON_ID = "bunny-guest";
const EMOJI_SETS = [
  { id: "emotion", label: { en: "Emotion", ko: "감정", es: "Emocion" }, items: ["😊", "😂", "😮", "😢", "😡", "👍"] },
  { id: "food", label: { en: "Food", ko: "음식", es: "Comida" }, items: ["🌮", "🍺", "🥛", "☕", "🍶", "🥃"] },
  { id: "places", label: { en: "Places", ko: "장소", es: "Lugares" }, items: ["🏠", "🏢", "🌳", "🎢", "🌊", "🏞️", "⛰️"] },
  { id: "animals", label: { en: "Animals", ko: "동물", es: "Animales" }, items: ["🐶", "🐱", "🐮", "🐕", "🐔", "🐷", "🦊", "🦁", "🐯", "🐰"] },
  { id: "misc", label: { en: "Other", ko: "기타", es: "Otros" }, items: ["❤️", "✔️", "⭐", "☀️", "🌙"] },
];
const BUILTIN_AVATAR_PRESETS = [
  { id: "man01", short: "M1", label: "Man 1", imagePath: "/static/avatars/man01.png?v=20260319-ui-service-53" },
  { id: "man02", short: "M2", label: "Man 2", imagePath: "/static/avatars/man02.png?v=20260319-ui-service-53" },
  { id: "man03", short: "M3", label: "Man 3", imagePath: "/static/avatars/man03.png?v=20260319-ui-service-53" },
  { id: "man04", short: "M4", label: "Man 4", imagePath: "/static/avatars/man04.png?v=20260319-ui-service-53" },
  { id: "man05", short: "M5", label: "Man 5", imagePath: "/static/avatars/man05.png?v=20260319-ui-service-53" },
  { id: "man06", short: "M6", label: "Man 6", imagePath: "/static/avatars/man06.png?v=20260319-ui-service-53" },
  { id: "man07", short: "M7", label: "Man 7", imagePath: "/static/avatars/man07.png?v=20260319-ui-service-53" },
  { id: "man08", short: "M8", label: "Man 8", imagePath: "/static/avatars/man08.png?v=20260319-ui-service-53" },
  { id: "woman01", short: "W1", label: "Woman 1", imagePath: "/static/avatars/woman01.png?v=20260319-ui-service-53" },
  { id: "woman02", short: "W2", label: "Woman 2", imagePath: "/static/avatars/woman02.png?v=20260319-ui-service-53" },
  { id: "woman03", short: "W3", label: "Woman 3", imagePath: "/static/avatars/woman03.png?v=20260319-ui-service-53" },
  { id: "woman04", short: "W4", label: "Woman 4", imagePath: "/static/avatars/woman04.png?v=20260319-ui-service-53" },
  { id: "woman05", short: "W5", label: "Woman 5", imagePath: "/static/avatars/woman05.png?v=20260319-ui-service-53" },
  { id: "woman06", short: "W6", label: "Woman 6", imagePath: "/static/avatars/woman06.png?v=20260319-ui-service-53" },
  { id: "woman07", short: "W7", label: "Woman 7", imagePath: "/static/avatars/woman07.png?v=20260319-ui-service-53" },
  { id: "woman08", short: "W8", label: "Woman 8", imagePath: "/static/avatars/woman08.png?v=20260319-ui-service-53" },
];
const MAX_REGISTERABLE_AVATARS = BUILTIN_AVATAR_PRESETS.length;
const UI_COPY = {
  en: {
    speak: "Speak",
    stop: "Stop",
    inviteButton: "Invite",
    exitButton: "Exit",
    fileButton: "File",
    emojiButton: "Emoji",
    sendButton: "Send",
    emojiSearchPlaceholder: "Search text or emoji",
    micJoinFirst: "Join a room before starting your microphone.",
    micReady: "Ready. Start your microphone when it is your turn to speak.",
    micLiveFor: "Microphone live for {language}.",
    micRequestPermission: "Requesting microphone permission...",
    micSpeakingNow: "{name} is now speaking into the realtime room.",
    micStopped: "Microphone stopped. Another participant can speak now.",
    micClosed: "Room connection closed.",
    micReconnect: "Reconnect to the room to speak again.",
    textShellTitle: "Type A Message",
    textJoinFirst: "Join a room before sending a text turn.",
    textJoinFirstExtended: "Join a room before sending a text, image, or file.",
    textSending: "Sending text turn...",
    textUploadingFile: "Uploading file...",
    textReady: "Press Send or Enter to add this sentence to the room.",
    textPrompt: "",
    textPlaceholder:
      "Pulsa el micrófono y habla por turnos.\nEscribe aquí (Enter)",
    textSent: "Text turn sent to the room.",
    textMessageFirst: "Type a message first.",
    turnWaitingTitle: "Waiting for room connection",
    turnWaitingBody: "Join the same room on two browsers, then let one speaker talk while the other listens.",
    turnReconnectTitle: "Reconnecting room",
    turnReconnectBodyAttempt:
      "Connection dropped. Retrying room socket now (attempt {attempt}).",
    turnReconnectBodyIdle: "Room socket is offline. Rejoin or wait for reconnect.",
    turnSpeakingTitle: "You are speaking",
    turnSpeakingBody:
      "Finish your sentence, then press Stop so the other speaker can take the next turn.",
    turnStartingTitle: "Your microphone is starting",
    turnStartingBody:
      "Speech is being captured. Keep speaking naturally until you finish the turn.",
    turnPartnerSpeakingTitle: "{name} is speaking",
    turnPartnerSpeakingBody:
      "Listen for the translation and wait until {name} finishes before you start your microphone.",
    turnWaitingPartnerTitle: "Waiting for the second speaker",
    turnWaitingPartnerBody:
      "Share the private invite link so the other Korean or Spanish speaker can join this room.",
    turnYourTurnTitle: "Your turn is available",
    turnYourTurnBody:
      "If you are ready, press Speak and talk in {language} while {name} listens.",
    inviteTitle: "Invite another participant",
    inviteBody: "Share this room by email or text so the other person can join right away.",
    inviteOpenLink: "Open invite link",
    inviteRoomCode: "Private invite",
    inviteEmail: "Email Invite",
    inviteSms: "Text Invite",
    inviteShare: "Share Link",
    inviteCopy: "Copy Link",
    inviteCopied: "Invite link copied.",
    inviteRoomCopied: "Private invite copied.",
    inviteEmailSubject: "Join my Bunny conversation room",
    inviteEmailBody:
      "Join my Bunny conversation room.%0A%0AOpen this private invite: {url}",
    inviteSmsBody: "Join my private Bunny invite: {url}",
    appShareShare: "Share",
    hostStatusChecking: "Checking",
    hostStatusOnline: "Online",
    hostStatusOffline: "Offline",
  },
  ko: {
    speak: "말하기",
    stop: "중지",
    inviteButton: "Invite",
    exitButton: "Exit",
    fileButton: "File",
    emojiButton: "이모티콘",
    sendButton: "Send",
    emojiSearchPlaceholder: "텍스트 또는 이모지로 검색",
    micJoinFirst: "마이크를 시작하려면 먼저 방에 참가하세요.",
    micReady: "준비되었습니다. 내 차례가 되면 Speak를 눌러 말하세요.",
    micLiveFor: "{language} 마이크가 켜졌습니다.",
    micRequestPermission: "마이크 권한을 요청하는 중입니다...",
    micSpeakingNow: "{name} 님의 음성을 실시간 방에 전송하는 중입니다.",
    micStopped: "마이크가 중지되었습니다. 이제 다른 참가자가 말할 수 있습니다.",
    micClosed: "방 연결이 종료되었습니다.",
    micReconnect: "다시 말하려면 방에 재연결하세요.",
    textShellTitle: "텍스트 입력",
    textJoinFirst: "텍스트를 보내려면 먼저 방에 참가하세요.",
    textJoinFirstExtended: "텍스트, 이미지, 파일을 보내려면 먼저 방에 참가하세요.",
    textSending: "텍스트를 보내는 중입니다...",
    textUploadingFile: "파일을 업로드하는 중입니다...",
    textReady: "Send 버튼이나 Enter 키로 이 문장을 방에 보낼 수 있습니다.",
    textPrompt: "",
    textPlaceholder:
      "텍스트 입력(음성통화는 마이크)",
    textSent: "텍스트 메시지를 방으로 보냈습니다.",
    textMessageFirst: "먼저 보낼 문장을 입력하세요.",
    turnWaitingTitle: "방 연결을 기다리는 중",
    turnWaitingBody:
      "두 브라우저에서 같은 방에 참가한 뒤, 한 명이 말하면 다른 한 명이 듣도록 진행하세요.",
    turnReconnectTitle: "방에 다시 연결하는 중",
    turnReconnectBodyAttempt: "연결이 끊겨 다시 시도 중입니다. ({attempt}회)",
    turnReconnectBodyIdle: "방 소켓이 오프라인입니다. 다시 참가하거나 재연결을 기다리세요.",
    turnSpeakingTitle: "지금 말하는 중입니다",
    turnSpeakingBody: "문장을 마친 뒤 Stop을 눌러 다음 사람에게 차례를 넘기세요.",
    turnStartingTitle: "마이크를 시작하는 중",
    turnStartingBody: "음성을 수집하고 있습니다. 턴이 끝날 때까지 자연스럽게 말하세요.",
    turnPartnerSpeakingTitle: "{name} 님이 말하는 중입니다",
    turnPartnerSpeakingBody:
      "{name} 님이 말을 마칠 때까지 번역을 들으면서 기다린 뒤 Speak를 눌러 주세요.",
    turnWaitingPartnerTitle: "다른 참가자를 기다리는 중",
    turnWaitingPartnerBody:
      "다른 한국어 또는 스페인어 사용자가 이 방에 들어올 수 있도록 비공개 초대 링크를 공유하세요.",
    turnYourTurnTitle: "이제 말할 수 있습니다",
    turnYourTurnBody: "준비되면 Speak를 누르고 {name} 님이 듣는 동안 {language}로 말하세요.",
    inviteTitle: "다른 참가자 초대",
    inviteBody: "이메일이나 문자로 방 링크를 보내면 상대방이 바로 참가할 수 있습니다.",
    inviteOpenLink: "초대 링크 열기",
    inviteRoomCode: "비공개 초대",
    inviteEmail: "이메일 초대",
    inviteSms: "문자 초대",
    inviteShare: "링크 공유",
    inviteCopy: "링크 복사",
    inviteCopied: "초대 링크를 복사했습니다.",
    inviteRoomCopied: "비공개 초대 링크를 복사했습니다.",
    inviteEmailSubject: "Bunny 대화방에 초대합니다",
    inviteEmailBody:
      "Bunny 대화방에 참가해 주세요.%0A%0A비공개 초대 링크: {url}",
    inviteSmsBody: "Bunny 비공개 초대 링크로 참가하세요: {url}",
    appShareShare: "Share",
    hostStatusChecking: "Checking",
    hostStatusOnline: "Online",
    hostStatusOffline: "Offline",
  },
  es: {
    speak: "Hablar",
    stop: "Detener",
    inviteButton: "Invitar",
    exitButton: "Salir",
    fileButton: "Archivo",
    emojiButton: "Emoticono",
    sendButton: "Enviar",
    emojiSearchPlaceholder: "Buscar texto o emoji",
    micJoinFirst: "Primero entra en la sala para usar el microfono.",
    micReady: "Todo listo. Cuando sea tu turno, pulsa Speak para hablar.",
    micLiveFor: "Microfono activo para {language}.",
    micRequestPermission: "Solicitando permiso para usar el microfono...",
    micSpeakingNow: "{name} esta hablando ahora en la sala en tiempo real.",
    micStopped: "Microfono detenido. Ahora la otra persona puede hablar.",
    micClosed: "La conexion de la sala se ha cerrado.",
    micReconnect: "Vuelve a conectarte a la sala para hablar otra vez.",
    textShellTitle: "Escribe un mensaje",
    textJoinFirst: "Primero entra en la sala para enviar un mensaje de texto.",
    textJoinFirstExtended: "Primero entra en la sala para enviar texto, imagenes o archivos.",
    textSending: "Enviando el mensaje...",
    textUploadingFile: "Subiendo archivo...",
    textReady: "Pulsa Send o Enter para enviar esta frase a la sala.",
    textPrompt: "",
    textPlaceholder:
      "Texto (micrófono de llamda)",
    textSent: "El mensaje de texto se envio a la sala.",
    textMessageFirst: "Primero escribe un mensaje.",
    turnWaitingTitle: "Esperando la conexion de la sala",
    turnWaitingBody:
      "Entren en la misma sala desde dos navegadores y dejen que una persona hable mientras la otra escucha.",
    turnReconnectTitle: "Reconectando la sala",
    turnReconnectBodyAttempt:
      "La conexion se corto. Intentando reconectar la sala ahora (intento {attempt}).",
    turnReconnectBodyIdle:
      "El socket de la sala esta desconectado. Vuelve a entrar o espera la reconexion.",
    turnSpeakingTitle: "Estas hablando",
    turnSpeakingBody:
      "Cuando termines la frase, pulsa Stop para que la otra persona tome el siguiente turno.",
    turnStartingTitle: "Tu microfono esta iniciando",
    turnStartingBody:
      "Se esta capturando tu voz. Habla con naturalidad hasta terminar el turno.",
    turnPartnerSpeakingTitle: "{name} esta hablando",
    turnPartnerSpeakingBody:
      "Escucha la traduccion y espera a que {name} termine antes de pulsar Speak.",
    turnWaitingPartnerTitle: "Esperando a la segunda persona",
    turnWaitingPartnerBody:
      "Comparte el enlace privado para que la otra persona en coreano o espanol pueda entrar.",
    turnYourTurnTitle: "Tu turno esta disponible",
    turnYourTurnBody:
      "Cuando quieras, pulsa Speak y habla en {language} mientras {name} escucha.",
    inviteTitle: "Invitar a otra persona",
    inviteBody: "Comparte esta sala por correo o mensaje para que la otra persona entre enseguida.",
    inviteOpenLink: "Abrir enlace de invitacion",
    inviteRoomCode: "Invitacion privada",
    inviteEmail: "Invitar por correo",
    inviteSms: "Invitar por mensaje",
    inviteShare: "Compartir enlace",
    inviteCopy: "Copiar enlace",
    inviteCopied: "El enlace de invitacion se copio.",
    inviteRoomCopied: "La invitacion privada se copio.",
    inviteEmailSubject: "Unete a mi sala de Bunny",
    inviteEmailBody:
      "Entra en mi sala de Bunny.%0A%0AUsa esta invitacion privada: {url}",
    inviteSmsBody: "Entra en mi sala Bunny con esta invitacion privada: {url}",
    appShareShare: "Share",
    hostStatusChecking: "Checking",
    hostStatusOnline: "Online",
    hostStatusOffline: "Offline",
  },
};

let currentRoom = null;
let selfParticipant = null;
let roomTitleEditing = false;
let socket = null;
let pingIntervalId = null;
let audioContext = null;
let mediaStream = null;
let processorNode = null;
let sourceNode = null;
let muteNode = null;
let latestSampleRate = 0;
let sessionStarted = false;
let liveTurnState = null;
let droppedChunkCount = 0;
let lastFinalPayload = null;
let roomConnectionGeneration = 0;
let reconnectTimeoutId = null;
let reconnectAttempt = 0;
let manualDisconnect = false;
let activeSpeaker = null;
let roomPreviewRequestId = 0;
let roomPreviewState = null;
let appendedTurnIds = new Set();
let lastAppendedTurnSignature = null;
let lastAppendedTurnAt = 0;
let conversationTurnCounter = 0;
let suggestedRoomId = "";
let latencyProbe = createLatencyProbe();
let textTurnSubmitting = false;
let attachmentTurnSubmitting = false;
let micStatusState = { key: "micJoinFirst", vars: {}, raw: "" };
let roomSessionReady = false;
let runtimePollIntervalId = null;
let historyPollIntervalId = null;
let serviceAvailability = { online: null, errorMessage: "" };
let currentUser = null;
let currentGuest = null;
let notifications = [];
let webPushConfig = { enabled: false, configured: false, supported: false, public_key: null };
let webPushSubscribed = false;
let serviceWorkerRegistrationPromise = null;
let roomHistory = [];
let selectedHistoryRoomId = "";
let selectedHistoryDetail = null;
let endedRoomIds = new Set();
let roomCapacity = 5;
let authMode = "login";
let profileEditorOpen = false;
let emojiPickerOpen = false;
const DEFAULT_PROFILE_BIO = "¡Vida radiante, una vez más!";

function isCompactMobile() {
  return window.matchMedia("(max-width: 720px)").matches;
}

function setSetupStatus(message) {
  if (!setupStatusEl) {
    return;
  }
  setupStatusEl.textContent = message || "";
  setupStatusEl.hidden = !message;
}

function setAccountStatus(message) {
  if (!accountStatusEl) {
    return;
  }
  accountStatusEl.textContent = message || "";
  accountStatusEl.hidden = !message;
}

function avatarCatalog() {
  return BUILTIN_AVATAR_PRESETS;
}

function avatarPresetFor(value) {
  return avatarCatalog().find((preset) => preset.id === value) || null;
}

function getAvatarFallbackLabel(value, fallback = "B") {
  const trimmed = String(value || fallback)
    .trim()
    .replace(/\s+/g, "");
  return (trimmed || fallback).slice(0, 2).toUpperCase();
}

function composePhoneNumber(countryCode, phoneValue) {
  const prefix = String(countryCode || "+52").trim() || "+52";
  const raw = String(phoneValue || "").trim();
  if (!raw) {
    return prefix;
  }

  const normalizedPlus = raw.startsWith("00") ? `+${raw.slice(2)}` : raw;
  if (normalizedPlus.startsWith("+")) {
    return normalizedPlus.replace(/[^\d+]/g, "");
  }

  const prefixDigits = prefix.replace(/[^\d]/g, "");
  const localDigits = raw.replace(/[^\d]/g, "");
  if (!localDigits) {
    return prefix;
  }
  if (prefixDigits && localDigits.startsWith(prefixDigits) && localDigits.length >= prefixDigits.length + 7) {
    return `+${localDigits}`;
  }
  return `${prefix}${localDigits}`;
}

function maskPhoneNumber(phone) {
  const normalized = String(phone || "").trim();
  if (!normalized) {
    return "";
  }
  const digits = normalized.replace(/[^\d]/g, "");
  if (!digits) {
    return normalized;
  }
  return digits.slice(-4);
}

function formatProfilePhoneNumber(phone) {
  const normalized = String(phone || "").trim();
  if (!normalized) {
    return "";
  }

  const digits = normalized.replace(/[^\d]/g, "");
  if (!digits) {
    return normalized;
  }

  const knownCountryCodes = ["82", "52", "34", "1"];
  const countryCode =
    knownCountryCodes.find((code) => digits.startsWith(code) && digits.length - code.length >= 8) ||
    (digits.length > 10 ? digits.slice(0, digits.length - 10) : "");
  const localDigits = countryCode ? digits.slice(countryCode.length) : digits;
  const countryPrefix = countryCode ? `+${countryCode}-` : "";

  if (localDigits.length >= 10) {
    const subscriber = localDigits.slice(-10);
    return `${countryPrefix}${subscriber.slice(0, 2)}-${subscriber.slice(2, 6)}-${subscriber.slice(6, 10)}`;
  }
  if (localDigits.length >= 6) {
    return `${countryPrefix}${localDigits.slice(0, 2)}-${localDigits.slice(2, 6)}-${localDigits.slice(6)}`;
  }
  return `${countryPrefix}${localDigits}`;
}

function localizedHomeNotice(name, language) {
  const safeName = truncateLabel(String(name || "Bunny User").trim() || "Bunny User", 10);
  if (language === "ko") {
    return `"${safeName}" 님의 홈`;
  }
  return `Inicio de "${safeName}"`;
}

function truncateLabel(value, maxLength = 10) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return "";
  }
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, Math.max(1, maxLength - 3)).trimEnd()}...`;
}

function currentProfileDraft() {
  const fallback = currentUser || currentGuest || null;
  const draftIcon = profileAvatarInput ? profileAvatarInput.value.trim() : fallback?.icon || "";
  return {
    display_name: displayNameInput?.value.trim() || fallback?.display_name || "",
    icon: draftIcon,
    bio: profileBioInput?.value.trim() || currentUser?.bio || DEFAULT_PROFILE_BIO,
    preferred_language: languageSelect?.value || currentUser?.preferred_language || "",
    notifications_enabled:
      profileNotificationSelect?.value === "no"
        ? false
        : currentUser?.notifications_enabled !== false,
  };
}

function showConversationScreen() {
  profileEditorOpen = false;
  if (serviceHeaderShellEl) {
    serviceHeaderShellEl.hidden = true;
  }
  if (serviceMainShellEl) {
    serviceMainShellEl.hidden = true;
  }
  if (mypageShellEl) {
    mypageShellEl.hidden = true;
  }
  if (chatScreenShellEl) {
    chatScreenShellEl.hidden = false;
  }
  syncHistoryPolling();
  syncScreenActionButtons();
}

function showMyPageScreen() {
  if (serviceHeaderShellEl) {
    serviceHeaderShellEl.hidden = !currentUser;
  }
  if (serviceMainShellEl) {
    serviceMainShellEl.hidden = !currentUser || !profileEditorOpen;
  }
  if (mypageShellEl) {
    mypageShellEl.hidden = !currentUser;
  }
  if (chatScreenShellEl) {
    chatScreenShellEl.hidden = true;
  }
  syncHistoryPolling();
  syncScreenActionButtons();
}

function toggleProfileEditor(forceOpen = !profileEditorOpen) {
  profileEditorOpen = Boolean(forceOpen && currentUser);
  if (serviceMainShellEl) {
    serviceMainShellEl.hidden = !profileEditorOpen;
  }
  if (editProfileButton) {
    editProfileButton.textContent = "";
    editProfileButton.setAttribute("aria-label", profileEditorOpen ? "Close" : "Edit");
    editProfileButton.setAttribute("title", profileEditorOpen ? "Close" : "Edit");
    editProfileButton.setAttribute("data-tooltip", profileEditorOpen ? "Close" : "Edit");
  }
}

function syncHistoryPolling() {
  const shouldPoll = Boolean(currentUser && mypageShellEl && !mypageShellEl.hidden);
  if (!shouldPoll) {
    if (historyPollIntervalId) {
      window.clearInterval(historyPollIntervalId);
      historyPollIntervalId = null;
    }
    return;
  }
  if (historyPollIntervalId) {
    return;
  }
  historyPollIntervalId = window.setInterval(() => {
    void loadRoomHistory().catch(() => {});
    void loadNotifications().catch(() => {});
  }, HISTORY_POLL_INTERVAL_MS);
}

function syncScreenActionButtons() {
  const hasActiveRoom = Boolean(currentRoom && selfParticipant && !endedRoomIds.has(currentRoom.room_id));
  if (closeMyPageButton) {
    closeMyPageButton.disabled = !hasActiveRoom;
  }
  if (exitRoomButton) {
    exitRoomButton.disabled = !hasActiveRoom;
  }
}

function clearAvatarVisual(element) {
  delete element.dataset.avatar;
  element.classList.remove("avatar-visual--image");
  element.style.backgroundImage = "";
}

function isGuestActor() {
  return Boolean(currentGuest && !currentUser);
}

function currentActor() {
  return currentUser || currentGuest;
}

function inviteCodeFromQuery() {
  const inviteCode = new URLSearchParams(window.location.search).get("invite")?.trim();
  if (!inviteCode) {
    return "";
  }
  return inviteCode;
}

function roomIdFromQuery() {
  const roomId = new URLSearchParams(window.location.search).get("room")?.trim();
  if (!roomId) {
    return "";
  }
  return roomId;
}

function currentInviteCode() {
  return currentRoom?.invite_code || roomPreviewState?.invite_code || inviteCodeFromQuery() || "";
}

function applyAvatar(element, iconValue, fallbackText = "B") {
  if (!element) {
    return;
  }
  clearAvatarVisual(element);
  if (iconValue === GUEST_ICON_ID) {
    element.classList.add("avatar-visual--image");
    element.style.backgroundImage = 'url("/static/bunny-transparent.png?v=20260319-ui-service-59")';
    element.textContent = "";
    element.setAttribute("aria-label", "Bunny guest avatar");
    return;
  }
  const preset = avatarPresetFor(iconValue);
  if (preset?.imagePath) {
    element.classList.add("avatar-visual--image");
    element.style.backgroundImage = `url("${preset.imagePath}")`;
    element.textContent = preset.short;
    element.setAttribute("aria-label", `${preset.label} avatar`);
    return;
  }
  element.textContent = getAvatarFallbackLabel(iconValue, fallbackText);
  element.setAttribute("aria-label", "User avatar");
}

function applySpeakerVisual(element, iconValue, language) {
  if (!element) {
    return;
  }
  clearAvatarVisual(element);
  if (iconValue === GUEST_ICON_ID) {
    element.classList.add("avatar-visual--image");
    element.style.backgroundImage = 'url("/static/bunny-transparent.png?v=20260319-ui-service-59")';
    element.textContent = "";
    element.setAttribute("aria-label", "Bunny guest speaker");
    return;
  }
  const preset = avatarPresetFor(iconValue);
  if (preset?.imagePath) {
    element.classList.add("avatar-visual--image");
    element.style.backgroundImage = `url("${preset.imagePath}")`;
    element.textContent = "";
    element.setAttribute("aria-label", `${preset.label} avatar`);
    return;
  }
  element.textContent = languageIcon(language);
  element.setAttribute("aria-label", `${languageLabel(language)} speaker`);
}

function isImageAttachment(attachment) {
  return Boolean(attachment?.content_type?.startsWith("image/"));
}

function attachmentHref(attachment) {
  if (!attachment?.file_url) {
    return "#";
  }
  if (/^https?:\/\//.test(attachment.file_url)) {
    return attachment.file_url;
  }
  return apiUrl(attachment.file_url);
}

function formatFileSize(sizeBytes) {
  const bytes = Number(sizeBytes || 0);
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "";
  }
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function renderRegisterAvatarPicker() {
  if (!registerAvatarGridEl) {
    return;
  }
  const avatars = avatarCatalog();
  const selectedAvatarId = avatarPresetFor(registerAvatarInput.value)?.id || DEFAULT_AVATAR_ID;
  registerAvatarGridEl.innerHTML = "";
  avatars.forEach((preset) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "auth-avatar-option";
    button.dataset.avatarOption = preset.id;
    const isSelected = preset.id === selectedAvatarId;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", isSelected ? "true" : "false");

    const badge = document.createElement("span");
    badge.className = "avatar-badge";
    applyAvatar(badge, preset.id, preset.label);

    button.append(badge);
    registerAvatarGridEl.appendChild(button);
  });
  if (avatarLibraryCountEl) {
    avatarLibraryCountEl.textContent = String(avatars.length);
  }
}

function renderProfileAvatarPicker() {
  if (!profileAvatarGridEl) {
    return;
  }
  const avatars = avatarCatalog();
  const selectedAvatarId = avatarPresetFor(profileAvatarInput?.value)?.id || DEFAULT_AVATAR_ID;
  profileAvatarGridEl.innerHTML = "";
  avatars.forEach((preset) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "auth-avatar-option";
    button.dataset.profileAvatarOption = preset.id;
    const isSelected = preset.id === selectedAvatarId;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", isSelected ? "true" : "false");

    const badge = document.createElement("span");
    badge.className = "avatar-badge";
    applyAvatar(badge, preset.id, preset.label);

    button.append(badge);
    profileAvatarGridEl.appendChild(button);
  });
  if (profileAvatarCountEl) {
    profileAvatarCountEl.textContent = String(avatars.length);
  }
}

function selectRegisterAvatar(avatarId) {
  const clickedAvatarId = avatarPresetFor(avatarId)?.id || DEFAULT_AVATAR_ID;
  const nextAvatarId =
    registerAvatarInput.value === clickedAvatarId ? DEFAULT_AVATAR_ID : clickedAvatarId;
  registerAvatarInput.value = nextAvatarId;
  renderRegisterAvatarPicker();
}

function selectProfileAvatar(avatarId) {
  const clickedAvatarId = avatarPresetFor(avatarId)?.id || DEFAULT_AVATAR_ID;
  const nextAvatarId =
    profileAvatarInput.value === clickedAvatarId ? DEFAULT_AVATAR_ID : clickedAvatarId;
  profileAvatarInput.value = nextAvatarId;
  renderProfileAvatarPicker();
  renderProfileSummary();
}

function setAuthMode(nextMode, options = {}) {
  const { clearStatus = true, focus = true } = options;
  authMode = nextMode === "register" ? "register" : "login";
  const showingRegister = authMode === "register";
  authScreenEl.classList.toggle("auth-screen--register", showingRegister);
  loginForm.hidden = showingRegister;
  registerForm.hidden = !showingRegister;
  if (authHeroTitleEl) {
    authHeroTitleEl.hidden = showingRegister;
  }
  if (authHeroCopyEl) {
    authHeroCopyEl.hidden = showingRegister;
  }
  if (clearStatus) {
    setAccountStatus("");
  }
  if (focus && !isCompactMobile()) {
    window.requestAnimationFrame(() => {
      if (showingRegister) {
        registerNameInput.focus();
      } else {
        loginPhoneInput.focus();
      }
    });
  }
}

bootstrap();

function bootstrap() {
  resetSetupFields();
  selectRegisterAvatar(DEFAULT_AVATAR_ID);
  setMicStatus("micJoinFirst");
  wireActions();
  void registerServiceWorker();
  renderAppShareRow();
  renderHostStatusDot();
  renderParticipants([]);
  renderInviteCard();
  renderMicButtons();
  renderTextComposer();
  updateTurnGuide();
  ensureDefaultRoomCode();
  hydrateRoomCodeFromQuery();
  renderInvitePreview();
  setAuthMode("login", { clearStatus: false, focus: false });
  renderAuthState();
  renderNotifications();
  renderWebPushState();
  renderHistoryList();
  renderHistoryDetail();
  void refreshRuntimeReadiness({ silent: true });
  void hydrateCurrentUser();
  startRuntimePolling();
  syncInitialViewport();
  if (!isCompactMobile()) {
    loginPhoneInput.focus();
  }
  window.addEventListener("pageshow", () => {
    resetSetupFields();
    selectRegisterAvatar(DEFAULT_AVATAR_ID);
    renderAppShareRow();
    renderHostStatusDot();
    renderInviteCard();
    renderMicButtons();
    renderTextComposer();
    ensureDefaultRoomCode();
    hydrateRoomCodeFromQuery();
    renderInvitePreview();
    renderAuthState();
    if (currentUser) {
      showMyPageScreen();
    }
    syncInitialViewport();
  });
  window.addEventListener("resize", () => {
    renderAppShareRow();
  });
  navigator.serviceWorker?.addEventListener("message", (event) => {
    if (event.data?.type === "notification_click" && event.data.url) {
      window.location.href = event.data.url;
    }
  });
}

function syncInitialViewport() {
  if (!isCompactMobile()) {
    return;
  }
  if (document.activeElement instanceof HTMLElement) {
    document.activeElement.blur();
  }
  window.requestAnimationFrame(() => {
    window.scrollTo(0, 0);
  });
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return null;
  }
  if (!serviceWorkerRegistrationPromise) {
    serviceWorkerRegistrationPromise = navigator.serviceWorker
      .register("/sw.js")
      .then(async (registration) => {
        await navigator.serviceWorker.ready;
        return registration;
      })
      .catch(() => null);
  }
  return serviceWorkerRegistrationPromise;
}

function browserSupportsWebPush() {
  return Boolean(
    "serviceWorker" in navigator &&
      "PushManager" in window &&
      "Notification" in window,
  );
}

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const normalized = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = window.atob(normalized);
  return Uint8Array.from(raw, (char) => char.charCodeAt(0));
}

function renderWebPushState() {
  const browserSupported = browserSupportsWebPush();
  const permission = browserSupported ? Notification.permission : "unsupported";
  const notificationsEnabled = currentUser?.notifications_enabled !== false;
  const canToggle = Boolean(currentUser);

  if (webPushStatusEl) {
    let statusText = "Web Push Off";
    if (!currentUser) {
      statusText = "Login required";
    } else if (!notificationsEnabled) {
      statusText = "Notifications Off";
    } else if (!browserSupported) {
      statusText = "Browser unsupported";
    } else if (!webPushConfig.configured) {
      statusText = "Server not configured";
    } else if (!webPushConfig.enabled) {
      statusText = "Push sender unavailable";
    } else if (permission === "denied") {
      statusText = "Permission denied";
    } else if (webPushSubscribed) {
      statusText = "Web Push On";
    } else if (permission === "granted") {
      statusText = "Ready to subscribe";
    } else {
      statusText = "Permission needed";
    }
    webPushStatusEl.textContent = statusText;
  }

  if (webPushToggleButton) {
    webPushToggleButton.disabled = !canToggle;
    if (!currentUser) {
      webPushToggleButton.textContent = "Enable Push";
    } else if (notificationsEnabled) {
      webPushToggleButton.textContent = "Disable Push";
    } else if (webPushSubscribed) {
      webPushToggleButton.textContent = "Disable Push";
    } else {
      webPushToggleButton.textContent = "Enable Push";
    }
  }
  if (notificationsButton && currentUser) {
    renderNotifications();
  }
}

async function loadWebPushConfig() {
  if (!currentUser) {
    webPushConfig = { enabled: false, configured: false, supported: false, public_key: null };
    webPushSubscribed = false;
    renderWebPushState();
    return;
  }
  webPushConfig = await requestJson("/api/me/web-push/config");
  await syncExistingWebPushSubscription();
}

async function syncExistingWebPushSubscription() {
  if (!currentUser || !browserSupportsWebPush() || !webPushConfig.enabled || !webPushConfig.public_key) {
    webPushSubscribed = false;
    renderWebPushState();
    return;
  }
  const registration = await registerServiceWorker();
  const subscription = registration ? await registration.pushManager.getSubscription() : null;
  if (currentUser.notifications_enabled === false) {
    if (subscription) {
      await deleteWebPushSubscriptionOnServer(subscription.endpoint).catch(() => {});
      await subscription.unsubscribe().catch(() => {});
    }
    webPushSubscribed = false;
    renderWebPushState();
    return;
  }
  webPushSubscribed = Boolean(subscription);
  if (subscription) {
    await requestJson("/api/me/web-push/subscriptions", {
      method: "POST",
      body: JSON.stringify({ subscription: subscription.toJSON() }),
    });
  }
  renderWebPushState();
}

async function deleteWebPushSubscriptionOnServer(endpoint) {
  await requestJson("/api/me/web-push/subscriptions", {
    method: "DELETE",
    body: JSON.stringify({ endpoint }),
  });
}

async function persistNotificationPreference(enabled) {
  if (!currentUser) {
    throw new Error("Login required.");
  }
  const session = await requestJson("/api/auth/me", {
    method: "PATCH",
    body: JSON.stringify({
      display_name: currentUser.display_name,
      icon: currentUser.icon || "",
      bio: currentUser.bio || "",
      preferred_language: currentUser.preferred_language || null,
      notifications_enabled: enabled,
    }),
  });
  currentUser = session.user;
  syncProfileIntoSetup();
  renderAuthState();
  renderNotifications();
  return session.user;
}

async function syncWebPushSubscriptionWithPreference({ requestPermission = false } = {}) {
  if (!currentUser) {
    throw new Error("Login required.");
  }
  if (!browserSupportsWebPush() || !webPushConfig.enabled || !webPushConfig.public_key) {
    webPushSubscribed = false;
    renderWebPushState();
    return;
  }

  const registration = await registerServiceWorker();
  if (!registration) {
    throw new Error("Service worker registration failed.");
  }

  let subscription = await registration.pushManager.getSubscription();
  if (currentUser.notifications_enabled === false) {
    if (subscription) {
      await deleteWebPushSubscriptionOnServer(subscription.endpoint).catch(() => {});
      await subscription.unsubscribe().catch(() => {});
    }
    webPushSubscribed = false;
    renderWebPushState();
    return;
  }

  if (subscription) {
    await requestJson("/api/me/web-push/subscriptions", {
      method: "POST",
      body: JSON.stringify({ subscription: subscription.toJSON() }),
    });
    webPushSubscribed = true;
    renderWebPushState();
    return;
  }

  let permission = Notification.permission;
  if (permission === "default" && requestPermission) {
    permission = await Notification.requestPermission();
  }
  if (permission !== "granted") {
    webPushSubscribed = false;
    renderWebPushState();
    if (requestPermission) {
      throw new Error("Notification permission was not granted.");
    }
    return;
  }

  subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(webPushConfig.public_key),
  });
  await requestJson("/api/me/web-push/subscriptions", {
    method: "POST",
    body: JSON.stringify({ subscription: subscription.toJSON() }),
  });
  webPushSubscribed = true;
  renderWebPushState();
}

async function toggleWebPushSubscription() {
  if (!currentUser) {
    throw new Error("Login required.");
  }
  const nextEnabled = currentUser.notifications_enabled === false;
  await persistNotificationPreference(nextEnabled);
  try {
    await syncWebPushSubscriptionWithPreference({ requestPermission: nextEnabled });
  } finally {
    await loadNotifications();
  }
}

async function hydrateCurrentUser() {
  try {
    const session = await requestJson("/api/auth/me");
    currentGuest = null;
    currentUser = session.user;
    await clearActiveRoomSession();
    resetHistorySelection();
    setAccountStatus("");
    syncProfileIntoSetup();
    renderAuthState();
    showMyPageScreen();
    await loadRoomHistory();
    await loadNotifications();
    await loadWebPushConfig();
    await maybeAutoEnterInvitedRoom();
  } catch {
    currentUser = null;
    notifications = [];
    webPushSubscribed = false;
    syncProfileIntoSetup();
    renderAuthState();
    renderNotifications();
    renderWebPushState();
    renderHistoryList();
    renderHistoryDetail();
  }
}

function syncProfileIntoSetup() {
  const actor = currentActor();
  if (actor) {
    displayNameInput.value = actor.display_name;
    displayNameInput.readOnly = false;
    if (profileBioInput) {
      profileBioInput.value = currentUser?.bio || DEFAULT_PROFILE_BIO;
    }
    if (profileNotificationSelect) {
      profileNotificationSelect.value = currentUser?.notifications_enabled === false ? "no" : "yes";
    }
    if (currentUser) {
      languageSelect.value = currentUser.preferred_language || "";
      profileAvatarInput.value = currentUser.icon || DEFAULT_AVATAR_ID;
    } else {
      languageSelect.value = "";
      profileAvatarInput.value = actor.icon || DEFAULT_AVATAR_ID;
    }
    renderProfileAvatarPicker();
    renderProfileSummary();
    return;
  }
  displayNameInput.value = "";
  displayNameInput.readOnly = false;
  if (profileBioInput) {
    profileBioInput.value = DEFAULT_PROFILE_BIO;
  }
  if (profileNotificationSelect) {
    profileNotificationSelect.value = "yes";
  }
  languageSelect.value = "";
  if (profileAvatarInput) {
    profileAvatarInput.value = DEFAULT_AVATAR_ID;
  }
  renderProfileAvatarPicker();
  renderProfileSummary();
}

function resetHistorySelection() {
  selectedHistoryRoomId = "";
  selectedHistoryDetail = null;
}

async function clearActiveRoomSession({ clearInvite = false } = {}) {
  await stopStreaming().catch(() => {});
  await disconnectRoomSocket({ intentional: true }).catch(() => {});
  currentRoom = null;
  selfParticipant = null;
  activeSpeaker = null;
  roomPreviewState = null;
  clearConversation();
  hideLiveCaption();
  renderParticipants([]);
  renderAppShareRow();
  renderInviteCard();
  renderRoomHeader();
  renderMicButtons();
  renderTextComposer();
  updateTurnGuide();
  if (clearInvite) {
    const url = new URL(window.location.href);
    url.searchParams.delete("room");
    url.searchParams.delete("invite");
    window.history.replaceState({}, "", url);
  }
}

function renderProfileSummary() {
  const draft = currentProfileDraft();
  applyAvatar(profileAvatarPreviewEl, draft.icon, draft.display_name || "B");
  if (profilePhoneTextEl) {
    profilePhoneTextEl.textContent = currentUser ? formatProfilePhoneNumber(currentUser.phone) : "Guest access";
  }
  if (profileBioPreviewEl) {
    profileBioPreviewEl.textContent = draft.bio || DEFAULT_PROFILE_BIO;
  }
  if (saveProfileButton) {
    saveProfileButton.textContent = "";
    saveProfileButton.setAttribute("aria-label", "Save");
    saveProfileButton.setAttribute("title", "Save");
    saveProfileButton.setAttribute("data-tooltip", "Save");
    saveProfileButton.disabled = !currentUser;
  }
}

function renderAuthState() {
  const actor = currentActor();
  const hasActor = Boolean(actor);
  const invitedInviteCode = inviteCodeFromQuery();
  authScreenEl.hidden = hasActor;
  serviceScreenEl.hidden = !hasActor;
  authGuestShellEl.hidden = false;
  accountSessionShellEl.hidden = !hasActor;
  if (serviceHeaderShellEl) {
    serviceHeaderShellEl.hidden = !hasActor || Boolean(chatScreenShellEl && !chatScreenShellEl.hidden);
  }
  if (guestInviteCardEl) {
    guestInviteCardEl.hidden = hasActor || !invitedInviteCode;
  }
  if (guestInviteRoomEl && invitedInviteCode) {
    guestInviteRoomEl.textContent = "Open your private invite to join this room.";
  }
  if (!hasActor) {
    showConversationScreen();
    if (serviceMainShellEl) {
      serviceMainShellEl.hidden = true;
    }
    if (mypageShellEl) {
      mypageShellEl.hidden = true;
    }
    if (chatScreenShellEl) {
      chatScreenShellEl.hidden = true;
    }
  }
  if (!hasActor) {
    profileEditorOpen = false;
    applyAvatar(sessionAvatarEl, DEFAULT_AVATAR_ID, "B");
    sessionNameEl.textContent = "Bunny User";
    sessionPhoneEl.textContent = "";
    if (sessionHomeNoticeEl) {
      sessionHomeNoticeEl.textContent = "";
    }
    if (sessionBioEl) {
      sessionBioEl.textContent = "";
    }
    if (openMyPageButton) {
      openMyPageButton.hidden = true;
    }
    if (editProfileButton) {
      editProfileButton.hidden = true;
      editProfileButton.textContent = "";
      editProfileButton.setAttribute("aria-label", "Edit");
      editProfileButton.setAttribute("title", "Edit");
      editProfileButton.setAttribute("data-tooltip", "Edit");
    }
    if (logoutButton) {
      logoutButton.textContent = "";
      logoutButton.setAttribute("aria-label", "Logout");
      logoutButton.setAttribute("title", "Logout");
      logoutButton.setAttribute("data-tooltip", "Logout");
    }
    if (notificationsButton) {
      notificationsButton.hidden = true;
      notificationsButton.removeAttribute("data-unread-count");
    }
    syncHistoryPolling();
    syncScreenActionButtons();
    return;
  }
  applyAvatar(sessionAvatarEl, actor.icon, actor.display_name);
  sessionNameEl.textContent = actor.display_name;
  sessionPhoneEl.textContent = currentUser ? maskPhoneNumber(currentUser.phone) : "Guest access";
  if (sessionHomeNoticeEl) {
    sessionHomeNoticeEl.textContent = localizedHomeNotice(
      actor.display_name,
      currentUser?.preferred_language || actor.preferred_language || "es",
    );
  }
  if (sessionBioEl) {
    sessionBioEl.textContent = currentUser?.bio || DEFAULT_PROFILE_BIO;
  }
  if (openMyPageButton) {
    openMyPageButton.hidden = !currentUser;
    openMyPageButton.textContent = "";
    openMyPageButton.setAttribute("aria-label", "Chatting Lists");
    openMyPageButton.setAttribute("title", "Chatting Lists");
    openMyPageButton.setAttribute("data-tooltip", "Chatting Lists");
  }
  if (notificationsButton) {
    notificationsButton.hidden = !currentUser;
  }
  if (editProfileButton) {
    editProfileButton.hidden = !currentUser;
    editProfileButton.textContent = "";
    editProfileButton.setAttribute("aria-label", profileEditorOpen ? "Close" : "Edit");
    editProfileButton.setAttribute("title", profileEditorOpen ? "Close" : "Edit");
    editProfileButton.setAttribute("data-tooltip", profileEditorOpen ? "Close" : "Edit");
  }
  if (logoutButton) {
    logoutButton.textContent = "";
    logoutButton.setAttribute("aria-label", currentUser ? "Logout" : "Leave");
    logoutButton.setAttribute("title", currentUser ? "Logout" : "Leave");
    logoutButton.setAttribute("data-tooltip", currentUser ? "Logout" : "Leave");
  }
  renderProfileSummary();
  syncHistoryPolling();
  syncScreenActionButtons();
}

async function saveProfile() {
  if (!currentUser) {
    throw new Error("로그인 후 프로필을 수정할 수 있습니다.");
  }
  const previousNotificationsEnabled = currentUser.notifications_enabled !== false;
  const draft = currentProfileDraft();
  if (!draft.display_name) {
    throw new Error("이름을 입력해 주세요.");
  }
  if (!draft.preferred_language) {
    throw new Error("기본 언어를 선택해 주세요.");
  }
  setSetupStatus("Saving your profile...");
  const payload = JSON.stringify({
    display_name: draft.display_name,
    icon: draft.icon,
    bio: draft.bio,
    preferred_language: draft.preferred_language,
    notifications_enabled: draft.notifications_enabled,
  });
  let session = null;
  let lastError = new Error("Profile save failed.");
  for (const method of ["PATCH", "PUT", "POST"]) {
    const response = await fetch(apiUrl("/api/auth/me"), {
      method,
      headers: { "Content-Type": "application/json" },
      body: payload,
      credentials: "same-origin",
    });
    if (response.ok) {
      session = await response.json();
      break;
    }
    let message = `Request failed with ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep fallback message.
    }
    lastError = new Error(message);
    if (response.status !== 405) {
      throw lastError;
    }
  }
  if (!session) {
    throw lastError;
  }
  currentUser = session.user;
  syncProfileIntoSetup();
  renderAuthState();
  await loadNotifications();
  try {
    await syncWebPushSubscriptionWithPreference({
      requestPermission: !previousNotificationsEnabled && draft.notifications_enabled,
    });
    setSetupStatus("개인정보를 저장했습니다.");
  } catch (error) {
    setSetupStatus(`개인정보를 저장했습니다. ${error.message}`);
  }
  toggleProfileEditor(false);
  showMyPageScreen();
}

async function registerAccount() {
  const password = registerPasswordInput.value;
  const passwordConfirm = registerPasswordConfirmInput.value;
  if (password !== passwordConfirm) {
    throw new Error("비밀번호 확인이 일치하지 않습니다.");
  }
  setAccountStatus("계정을 만드는 중입니다...");
  const session = await requestJson("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({
      display_name: registerNameInput.value.trim(),
      phone: composePhoneNumber(registerCountryCodeSelect?.value, registerPhoneInput.value),
      icon: registerAvatarInput.value.trim(),
      password,
    }),
  });
  currentGuest = null;
  currentUser = session.user;
  resetHistorySelection();
  registerForm.reset();
  selectRegisterAvatar(DEFAULT_AVATAR_ID);
  loginForm.reset();
  if (registerCountryCodeSelect) {
    registerCountryCodeSelect.value = "+52";
  }
  if (loginCountryCodeSelect) {
    loginCountryCodeSelect.value = "+52";
  }
  setAccountStatus("회원가입이 완료되었습니다.");
  await clearActiveRoomSession();
  syncProfileIntoSetup();
  showMyPageScreen();
  renderAuthState();
  ensureDefaultRoomCode();
  await loadRoomHistory();
  await loadNotifications();
  await loadWebPushConfig();
  await maybeAutoEnterInvitedRoom();
}

async function loginAccount() {
  setAccountStatus("로그인하는 중입니다...");
  const session = await requestJson("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({
      phone: composePhoneNumber(loginCountryCodeSelect?.value, loginPhoneInput.value),
      password: loginPasswordInput.value,
    }),
  });
  currentGuest = null;
  currentUser = session.user;
  resetHistorySelection();
  loginForm.reset();
  if (loginCountryCodeSelect) {
    loginCountryCodeSelect.value = "+52";
  }
  setAccountStatus("로그인되었습니다.");
  await clearActiveRoomSession();
  syncProfileIntoSetup();
  showMyPageScreen();
  renderAuthState();
  ensureDefaultRoomCode();
  await loadRoomHistory();
  await loadNotifications();
  await loadWebPushConfig();
  await maybeAutoEnterInvitedRoom();
}

async function logoutAccount() {
  if (!currentUser && currentGuest) {
    currentGuest = null;
    currentRoom = null;
    selfParticipant = null;
    activeSpeaker = null;
    roomPreviewState = null;
    clearConversation();
    hideLiveCaption();
    renderParticipants([]);
    renderAppShareRow();
    renderInviteCard();
    renderRoomHeader();
    renderMicButtons();
    renderTextComposer();
    updateTurnGuide();
    syncProfileIntoSetup();
    showMyPageScreen();
    setAuthMode("login", { clearStatus: false, focus: !isCompactMobile() });
    renderAuthState();
    setAccountStatus("Guest session ended.");
    resetSetupFields();
    hydrateRoomCodeFromQuery();
    return;
  }
  const response = await fetch(apiUrl("/api/auth/logout"), {
    method: "POST",
    credentials: "same-origin",
  });
  if (!response.ok && response.status !== 401) {
    throw new Error(`Logout failed with ${response.status}`);
  }
  await clearActiveRoomSession({ clearInvite: true });
  currentUser = null;
  notifications = [];
  webPushSubscribed = false;
  webPushConfig = { enabled: false, configured: false, supported: false, public_key: null };
  roomHistory = [];
  selectedHistoryRoomId = "";
  selectedHistoryDetail = null;
  endedRoomIds = new Set();
  setAccountStatus("로그아웃되었습니다.");
  syncProfileIntoSetup();
  showMyPageScreen();
  setAuthMode("login", { clearStatus: false, focus: !isCompactMobile() });
  renderAuthState();
  renderNotifications();
  renderWebPushState();
  renderHistoryList();
  renderHistoryDetail();
  resetSetupFields();
}

async function loadRoomHistory() {
  if (!currentUser) {
    roomHistory = [];
    selectedHistoryRoomId = "";
    selectedHistoryDetail = null;
    syncHistoryActionButtons();
    renderHistoryList();
    renderHistoryDetail();
    return;
  }
  roomHistory = await requestJson("/api/me/rooms");
  syncHistoryActionButtons();
  renderHistoryList();
  if (selectedHistoryRoomId && roomHistory.some((room) => room.room_id === selectedHistoryRoomId)) {
    if (selectedHistoryDetail?.room?.room_id === selectedHistoryRoomId) {
      renderHistoryDetail(selectedHistoryDetail);
      return;
    }
  } else {
    selectedHistoryDetail = null;
  }
  renderHistoryDetail(selectedHistoryDetail);
}

async function loadNotifications() {
  if (!currentUser) {
    notifications = [];
    renderNotifications();
    return;
  }
  notifications = await requestJson("/api/me/notifications");
  renderNotifications();
}

function notificationTypeLabel(notification) {
  switch (notification.notification_type) {
    case "invite":
      return "Invite";
    case "announcement":
      return "Notice";
    default:
      return "Message";
  }
}

function renderNotifications() {
  const notificationsEnabled = currentUser?.notifications_enabled !== false;
  const unreadCount = notificationsEnabled
    ? notifications.filter((item) => !item.read_at).length
    : 0;
  if (notificationsButton) {
    let pushState = notificationsEnabled ? "on" : "off";
    let buttonLabel = notificationsEnabled
      ? unreadCount
        ? `Disable Notifications · ${unreadCount}`
        : "Disable Notifications"
      : "Enable Notifications";
    if (!currentUser) {
      pushState = "unavailable";
      buttonLabel = "Notifications unavailable";
    }
    notificationsButton.textContent = "";
    notificationsButton.hidden = !currentUser;
    notificationsButton.setAttribute("aria-label", buttonLabel);
    notificationsButton.setAttribute("title", buttonLabel);
    notificationsButton.setAttribute("data-tooltip", buttonLabel);
    notificationsButton.setAttribute("data-unread-count", String(unreadCount));
    notificationsButton.setAttribute("data-push-state", pushState);
  }
  if (notificationUnreadBadgeEl) {
    notificationUnreadBadgeEl.hidden = unreadCount === 0;
    notificationUnreadBadgeEl.textContent = unreadCount === 1 ? "1 New" : `${unreadCount} New`;
  }
  if (markAllNotificationsReadButton) {
    markAllNotificationsReadButton.disabled = unreadCount === 0 || !currentUser;
  }
  renderHistoryList();
}

async function markNotificationRead(notificationId) {
  await requestJson(`/api/me/notifications/${encodeURIComponent(notificationId)}/read`, {
    method: "POST",
  });
  notifications = notifications.map((notification) =>
    notification.notification_id === notificationId
      ? { ...notification, read_at: new Date().toISOString() }
      : notification,
  );
  renderNotifications();
}

async function markAllNotificationsRead() {
  if (!currentUser) {
    return;
  }
  await requestJson("/api/me/notifications/read-all", { method: "POST" });
  notifications = notifications.map((notification) => ({
    ...notification,
    read_at: notification.read_at || new Date().toISOString(),
  }));
  renderNotifications();
}

function unreadNotificationCountForRoom(roomId) {
  if (!roomId || currentUser?.notifications_enabled === false) {
    return 0;
  }
  return notifications.filter(
    (notification) => notification.room_id === roomId && !notification.read_at,
  ).length;
}

async function markRoomNotificationsRead(roomId) {
  if (!currentUser || !roomId) {
    return;
  }
  const unreadRoomNotifications = notifications.filter(
    (notification) => notification.room_id === roomId && !notification.read_at,
  );
  if (!unreadRoomNotifications.length) {
    return;
  }
  await Promise.all(
    unreadRoomNotifications.map((notification) =>
      requestJson(`/api/me/notifications/${encodeURIComponent(notification.notification_id)}/read`, {
        method: "POST",
      }),
    ),
  );
  const readAt = new Date().toISOString();
  notifications = notifications.map((notification) =>
    notification.room_id === roomId && !notification.read_at
      ? { ...notification, read_at: readAt }
      : notification,
  );
  renderNotifications();
}

async function openNotification(notification) {
  if (!notification.read_at) {
    await markNotificationRead(notification.notification_id);
  }
  if (notification.room_id) {
    showMyPageScreen();
    await openRoomHistory(notification.room_id);
    historyListEl?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function renderHistoryList() {
  if (!historyListEl) {
    return;
  }
  historyListEl.innerHTML = "";
  if (!currentUser) {
    historyListEl.innerHTML =
      '<article class="history-empty">Select a room from your saved history.</article>';
    return;
  }
  if (!roomHistory.length) {
    historyListEl.innerHTML =
      '<article class="history-empty">No saved rooms yet.</article>';
    return;
  }
  roomHistory.forEach((room) => {
    const unreadCount = unreadNotificationCountForRoom(room.room_id);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `history-item${room.room_id === selectedHistoryRoomId ? " history-item--active" : ""}${unreadCount ? " history-item--unread" : ""}`;
    const avatar = createHistoryAvatarElement(room);
    const body = document.createElement("div");
    body.className = "history-item__body";
    body.innerHTML = `
      <div class="history-item__header">
        <p class="history-item__name" title="${escapeHtml(historyRoomTitle(room))}">${escapeHtml(historyRoomTitle(room))}</p>
        <div class="history-item__meta">
          ${unreadCount ? `<span class="history-item__badge" aria-label="Unread ${unreadCount}">${escapeHtml(String(unreadCount))}</span>` : ""}
          <p class="history-item__time">${escapeHtml(formatHistoryListTimestamp(room.last_activity_at))}</p>
        </div>
      </div>
      <p class="history-item__preview" title="${escapeHtml(historyPreviewText(room))}">${escapeHtml(historyPreviewText(room))}</p>
    `;
    button.append(avatar, body);
    button.addEventListener("click", () => {
      void openRoomHistory(room.room_id);
    });
    button.addEventListener("dblclick", () => {
      void resumeHistoryRoom(room.room_id).catch((error) => {
        setSetupStatus(error.message);
      });
    });
    historyListEl.appendChild(button);
  });
}

function historyPreviewFromTurn(turn) {
  if (!turn) {
    return "No conversation yet.";
  }
  if (turn.turn_type === "attachment") {
    return turn.attachment?.file_name || "Sent an attachment.";
  }
  return turn.source_text?.trim() || "No conversation yet.";
}

function summarizeHistoryDetail(detail) {
  const turns = detail?.turns || [];
  const latestTurn = turns[turns.length - 1] || null;
  const counterpartFromTurns =
    [...turns]
      .reverse()
      .map((turn) => turn.speaker)
      .find((speaker) => speaker?.participant_id !== detail.participant_id) || null;
  const counterpartFromParticipants =
    [...(detail?.room?.participants || [])]
      .reverse()
      .find((item) => item.participant_id !== detail.participant_id) || null;
  const counterpart = counterpartFromTurns || counterpartFromParticipants || null;
  return {
    room_id: detail.room.room_id,
    room_title: detail.room.title || "",
    status: detail.room.status,
    participant_count: detail.room.participant_count,
    turn_count: turns.length,
    counterpart_name: counterpart?.display_name || "Waiting for participant",
    counterpart_icon: counterpart?.icon || "",
    participant_visuals: (detail?.room?.participants || []).slice(0, 4).map((participant) => ({
      display_name: participant.display_name || "Speaker",
      icon: participant.icon || "",
    })),
    last_message: historyPreviewFromTurn(latestTurn),
    last_activity_at: latestTurn?.created_at || detail.room.last_activity_at,
  };
}

function mergeRoomHistorySummary(summary) {
  const index = roomHistory.findIndex((item) => item.room_id === summary.room_id);
  if (index === -1) {
    return;
  }
  roomHistory[index] = {
    ...roomHistory[index],
    ...summary,
  };
}

async function openRoomHistory(roomId) {
  selectedHistoryRoomId = roomId;
  selectedHistoryDetail = null;
  syncHistoryActionButtons();
  renderHistoryList();
  historyDetailEl.innerHTML =
    '<article class="history-empty">Loading conversation...</article>';
  try {
    const detail = await requestJson(`/api/me/rooms/${encodeURIComponent(roomId)}`);
    selectedHistoryDetail = detail;
    mergeRoomHistorySummary(summarizeHistoryDetail(detail));
    renderHistoryList();
    syncHistoryActionButtons();
    renderHistoryDetail(detail);
    void markRoomNotificationsRead(roomId).catch(() => {});
  } catch (error) {
    historyDetailEl.innerHTML = `<article class="history-empty">${escapeHtml(error.message)}</article>`;
  }
}

async function resumeHistoryRoom(roomId = selectedHistoryRoomId) {
  if (!roomId || !currentUser) {
    return;
  }
  if (currentRoom && selfParticipant && currentRoom.room_id === roomId && !endedRoomIds.has(roomId)) {
    await activateRoom(currentRoom, selfParticipant, false, { openChat: true });
    return;
  }

  const detail =
    selectedHistoryDetail?.room?.room_id === roomId
      ? selectedHistoryDetail
      : await requestJson(`/api/me/rooms/${encodeURIComponent(roomId)}`);
  selectedHistoryRoomId = roomId;
  selectedHistoryDetail = detail;
  mergeRoomHistorySummary(summarizeHistoryDetail(detail));
  renderHistoryList();
  renderHistoryDetail(detail);
  syncHistoryActionButtons();
  void markRoomNotificationsRead(roomId).catch(() => {});

  const inviteCode = detail.room.invite_code || "";
  if (!inviteCode) {
    throw new Error("This conversation can no longer be joined.");
  }
  if (!languageSelect.value) {
    languageSelect.value = inferInviteLanguage(detail.room);
  }
  await joinRoom({ inviteCodeOverride: inviteCode, autoInvite: true });
}

function renderHistoryDetail(detail = null) {
  if (!historyDetailEl) {
    return;
  }
  if (!currentUser) {
    historyDetailEl.innerHTML =
      '<article class="history-empty">Sign in to use My Page.</article>';
    return;
  }
  if (!detail) {
    historyDetailEl.innerHTML =
      '<article class="history-empty">Select a room to view the conversation.</article>';
    return;
  }

  const turnsMarkup = detail.turns.length
    ? [...detail.turns]
        .reverse()
        .map(
          (turn) => {
            const translationsMarkup = visibleTurnTranslations(turn)
              .map(
                ([language, translation]) =>
                  `<p class="history-turn__translation">${escapeHtml(language)}: ${escapeHtml(translation)}</p>`,
              )
              .join("");
            return `
              <article class="history-turn">
                <p class="history-turn__meta">${escapeHtml(turn.speaker.display_name)} · ${escapeHtml(turn.source_language)} · ${escapeHtml(formatDateTime(turn.created_at))}</p>
                ${
                  turn.turn_type === "attachment" && turn.attachment
                    ? `<p class="history-turn__source"><a href="${escapeHtml(attachmentHref(turn.attachment))}" target="_blank" rel="noreferrer">${escapeHtml(turn.attachment.file_name)}</a>${turn.attachment.size_bytes ? ` · ${escapeHtml(formatFileSize(turn.attachment.size_bytes))}` : ""}</p>`
                    : `<p class="history-turn__source">${escapeHtml(turn.source_text)}</p>`
                }
                ${translationsMarkup}
              </article>
            `;
          },
        )
        .join("")
    : '<article class="history-empty">No saved conversation yet.</article>';

  historyDetailEl.innerHTML = `
    <div class="history-detail__header">
      <div class="history-detail__copy">
        <h3 class="history-detail__title">${escapeHtml(historyRoomTitle(summarizeHistoryDetail(detail)))}</h3>
        <p class="history-detail__meta">Joined ${escapeHtml(formatDateTime(detail.joined_at))} · Last active ${escapeHtml(formatDateTime(detail.room.last_activity_at))}</p>
      </div>
    </div>
    ${turnsMarkup}
  `;
}

async function deleteRoomHistory(roomId) {
  const response = await fetch(apiUrl(`/api/me/rooms/${encodeURIComponent(roomId)}`), {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Delete failed with ${response.status}`);
  }
  const shouldClearInvite =
    currentRoom?.room_id === roomId ||
    selectedHistoryDetail?.room?.room_id === roomId ||
    roomIdFromQuery() === roomId;
  if (shouldClearInvite) {
    await clearActiveRoomSession({ clearInvite: true });
  }
  if (selectedHistoryRoomId === roomId) {
    selectedHistoryRoomId = "";
  }
  if (selectedHistoryDetail?.room?.room_id === roomId) {
    selectedHistoryDetail = null;
  }
  roomHistory = roomHistory.filter((room) => room.room_id !== roomId);
  renderHistoryList();
  renderHistoryDetail(selectedHistoryDetail);
  syncHistoryActionButtons();
  showMyPageScreen();
  await loadRoomHistory();
}

function syncHistoryActionButtons() {
  const hasSelection = Boolean(selectedHistoryRoomId);
  if (createHistoryButton) {
    createHistoryButton.disabled = !currentUser;
  }
  if (joinHistoryButton) {
    joinHistoryButton.disabled = !hasSelection;
  }
  if (downloadHistoryButton) {
    downloadHistoryButton.disabled = !hasSelection;
  }
  if (deleteHistoryButton) {
    deleteHistoryButton.disabled = !hasSelection;
  }
}

function formatDateTime(value) {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleString("ko-KR", {
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatHistoryListTimestamp(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const parts = new Intl.DateTimeFormat("ko-KR", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).formatToParts(date);
  const part = (type) => parts.find((item) => item.type === type)?.value || "";
  return `${part("month")}.${part("day")} ${part("hour")}:${part("minute")}`.trim();
}

function historyCounterpartName(room) {
  const name = room?.counterpart_name?.trim();
  if (!name || name === "Waiting for participant") {
    return "대화 상대 대기중";
  }
  return name;
}

function historyRoomTitle(room) {
  const title = room?.room_title?.trim();
  if (title) {
    return title;
  }
  return fallbackRoomTitle();
}

function normalizedTurnText(text) {
  return String(text || "").trim().replace(/\s+/g, " ");
}

function visibleTurnTranslations(turn) {
  const sourceText = normalizedTurnText(turn?.source_text);
  const sourceLanguage = String(turn?.source_language || "").trim();
  return Object.entries(turn?.translations || {}).filter(([language, translation]) => {
    const translatedText = normalizedTurnText(translation);
    if (!translatedText) {
      return false;
    }
    if (language === sourceLanguage) {
      return false;
    }
    if (translatedText === sourceText) {
      return false;
    }
    return true;
  });
}

function historyPreviewText(room) {
  const preview = room?.last_message?.trim();
  if (!preview || preview === "No conversation yet.") {
    return "아직 대화가 없습니다.";
  }
  if (preview === "Sent an attachment.") {
    return "파일을 보냈습니다.";
  }
  return preview;
}

function historyParticipantVisuals(room) {
  const visuals = Array.isArray(room?.participant_visuals)
    ? room.participant_visuals.filter((item) => item && (item.icon || item.display_name))
    : [];
  if (visuals.length) {
    return visuals.slice(0, 4);
  }
  const waitingCounterpart = !room?.counterpart_icon && historyCounterpartName(room) === "대화 상대 대기중";
  if (!waitingCounterpart && (room?.counterpart_icon || room?.counterpart_name)) {
    return [
      {
        display_name: historyCounterpartName(room),
        icon: room?.counterpart_icon || "",
      },
    ];
  }
  if (currentUser?.icon || currentUser?.display_name) {
    return [
      {
        display_name: currentUser.display_name || "Me",
        icon: currentUser.icon || "",
      },
    ];
  }
  return [{ display_name: "?", icon: "" }];
}

function createHistoryAvatarElement(room) {
  const visuals = historyParticipantVisuals(room);
  if (visuals.length <= 1) {
    const avatar = document.createElement("span");
    avatar.className = "history-item__avatar";
    const visual = visuals[0] || { display_name: "?", icon: "" };
    applyAvatar(avatar, visual.icon || "", visual.display_name || "?");
    return avatar;
  }

  const avatarGroup = document.createElement("span");
  avatarGroup.className = "history-item__avatar-group";
  visuals.slice(0, 4).forEach((visual, index) => {
    const avatar = document.createElement("span");
    avatar.className = "history-item__avatar history-item__avatar--mini";
    avatar.style.setProperty("--history-avatar-index", String(index));
    applyAvatar(avatar, visual.icon || "", visual.display_name || "?");
    avatarGroup.appendChild(avatar);
  });
  return avatarGroup;
}

async function shareCurrentInvite() {
  if (!currentRoom) {
    setSetupStatus("먼저 대화방을 만들거나 다시 들어간 뒤 초대해 주세요.");
    return;
  }
  const url = inviteUrlForRoom(currentInviteCode());
  const shareData = {
    title: "Bunny AI",
    text: `Join my Bunny private invite: ${url}`,
    url,
  };
  if (navigator.share) {
    await navigator.share(shareData);
    return;
  }
  await navigator.clipboard.writeText(url);
  setSetupStatus("Invite link copied.");
}

function wireActions() {
  showRegisterButton.addEventListener("click", () => {
    setAuthMode("register");
  });

  showLoginButton.addEventListener("click", () => {
    setAuthMode("login");
  });

  continueGuestButton?.addEventListener("click", () => {
    continueAsGuest().catch((error) => {
      setAccountStatus(error.message);
    });
  });

  registerAvatarGridEl.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
      return;
    }
    const button = event.target.closest("[data-avatar-option]");
    if (!(button instanceof HTMLElement)) {
      return;
    }
    selectRegisterAvatar(button.dataset.avatarOption || DEFAULT_AVATAR_ID);
  });

  profileAvatarGridEl?.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
      return;
    }
    const button = event.target.closest("[data-profile-avatar-option]");
    if (!(button instanceof HTMLElement)) {
      return;
    }
    selectProfileAvatar(button.dataset.profileAvatarOption || DEFAULT_AVATAR_ID);
  });

  registerForm.addEventListener("submit", (event) => {
    event.preventDefault();
    registerAccount().catch((error) => {
      setAccountStatus(error.message);
    });
  });

  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    loginAccount().catch((error) => {
      setAccountStatus(error.message);
    });
  });

  logoutButton.addEventListener("click", () => {
    logoutAccount().catch((error) => {
      setAccountStatus(error.message);
    });
  });

  openMyPageButton?.addEventListener("click", () => {
    if (!currentUser) {
      return;
    }
    toggleProfileEditor(false);
    showMyPageScreen();
    void loadRoomHistory();
    void loadNotifications();
  });

  notificationsButton?.addEventListener("click", () => {
    if (!currentUser) {
      return;
    }
    toggleWebPushSubscription().catch((error) => {
      setSetupStatus(error.message);
      renderWebPushState();
    });
  });

  webPushToggleButton?.addEventListener("click", () => {
    toggleWebPushSubscription().catch((error) => {
      setSetupStatus(error.message);
      renderWebPushState();
    });
  });

  editProfileButton?.addEventListener("click", () => {
    if (!currentUser) {
      return;
    }
    toggleProfileEditor();
    showMyPageScreen();
  });

  saveProfileButton?.addEventListener("click", () => {
    saveProfile().catch((error) => {
      setSetupStatus(error.message);
    });
  });

  closeMyPageButton?.addEventListener("click", () => {
    if (!currentRoom || !selfParticipant || endedRoomIds.has(currentRoom.room_id)) {
      return;
    }
    void activateRoom(currentRoom, selfParticipant, false, { openChat: true });
  });

  exitRoomButton?.addEventListener("click", () => {
    if (!currentUser) {
      return;
    }
    const activeRoomId = currentRoom?.room_id || "";
    if (activeRoomId) {
      selectedHistoryRoomId = activeRoomId;
      selectedHistoryDetail = null;
      void loadRoomHistory()
        .then(() => openRoomHistory(activeRoomId))
        .catch(() => {});
    }
    showMyPageScreen();
    void loadNotifications();
  });

  homeRoomButton?.addEventListener("click", () => {
    if (!currentUser) {
      return;
    }
    toggleProfileEditor(false);
    showMyPageScreen();
    void loadRoomHistory();
    void loadNotifications();
  });

  joinHistoryButton?.addEventListener("click", () => {
    if (!selectedHistoryRoomId) {
      return;
    }
    void resumeHistoryRoom(selectedHistoryRoomId).catch((error) => {
      setSetupStatus(error.message);
    });
  });

  downloadHistoryButton?.addEventListener("click", () => {
    if (!selectedHistoryRoomId) {
      return;
    }
    const confirmed = window.confirm("Download the selected conversation history?");
    if (!confirmed) {
      return;
    }
    window.location.href = apiUrl(`/api/me/rooms/${encodeURIComponent(selectedHistoryRoomId)}/download`);
  });

  deleteHistoryButton?.addEventListener("click", () => {
    if (!selectedHistoryRoomId) {
      return;
    }
    const confirmed = window.confirm("Delete the selected conversation history?");
    if (!confirmed) {
      return;
    }
    void deleteRoomHistory(selectedHistoryRoomId);
  });

  createHistoryButton?.addEventListener("click", () => {
    createRoom().catch((error) => {
      setSetupStatus(error.message);
      void refreshRuntimeReadiness({ silent: true });
    });
  });

  joinRoomButton?.addEventListener("click", () => {
    joinRoom().catch((error) => {
      setSetupStatus(error.message);
      void refreshRuntimeReadiness({ silent: true });
    });
  });

  roomCodeInput.addEventListener("input", () => {});

  languageSelect.addEventListener("change", () => {
    renderProfileSummary();
    rerenderLanguageDependentCopy();
  });

  displayNameInput?.addEventListener("input", () => {
    renderProfileSummary();
  });

  profileBioInput?.addEventListener("input", () => {
    renderProfileSummary();
  });

  roomCodeInput.addEventListener("blur", () => {});

  if (copyInviteButton) {
    copyInviteButton.addEventListener("click", async () => {
      if (!currentRoom) {
        return;
      }
      const inviteUrl = inviteUrlForRoom(currentInviteCode());
      await navigator.clipboard.writeText(inviteUrl);
      setSetupStatus(translateUi("inviteCopied"));
    });
  }

  shareAppButton?.addEventListener("click", async () => {
    await shareCurrentInvite();
  });

  chatInviteButton?.addEventListener("click", async () => {
    await shareCurrentInvite();
  });

  chatLanguageSelect?.addEventListener("change", () => {
    const nextLanguage = chatLanguageSelect.value;
    if (!nextLanguage) {
      return;
    }
    if (languageSelect) {
      languageSelect.value = nextLanguage;
    }
    if (currentUser) {
      currentUser = { ...currentUser, preferred_language: nextLanguage };
    }
    if (selfParticipant) {
      selfParticipant.language = nextLanguage;
    }
    if (currentRoom && selfParticipant) {
      currentRoom = {
        ...currentRoom,
        participants: currentRoom.participants.map((participant) =>
          participant.participant_id === selfParticipant.participant_id
            ? { ...participant, language: nextLanguage }
            : participant,
        ),
      };
    }
    renderParticipants(currentRoom?.participants || []);
    renderRoomHeader();
    rerenderLanguageDependentCopy();
    renderProfileSummary();
  });

  chatRoomTitleEditButton?.addEventListener("click", () => {
    if (!currentRoom) {
      return;
    }
    if (roomTitleEditing) {
      saveCurrentRoomTitle().catch((error) => {
        setSetupStatus(error.message);
      });
      return;
    }
    roomTitleEditing = true;
    renderRoomHeader();
    chatRoomTitleInput?.focus();
    chatRoomTitleInput?.select();
  });

  chatRoomTitleInput?.addEventListener("input", () => {
    if (chatRoomTitleInput.value.length > 80) {
      chatRoomTitleInput.value = chatRoomTitleInput.value.slice(0, 80);
    }
  });

  chatRoomTitleInput?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    saveCurrentRoomTitle().catch((error) => {
      setSetupStatus(error.message);
    });
  });

  if (inviteRoomCodeButton) {
    inviteRoomCodeButton.addEventListener("click", async () => {
      if (!currentRoom) {
        return;
      }
      await navigator.clipboard.writeText(inviteUrlForRoom(currentInviteCode()));
      setSetupStatus(translateUi("inviteRoomCopied"));
    });
  }

  if (emailInviteButton) {
    emailInviteButton.addEventListener("click", () => {
      if (!currentRoom) {
        return;
      }
      window.location.href = inviteEmailHref(currentInviteCode());
    });
  }

  if (smsInviteButton) {
    smsInviteButton.addEventListener("click", () => {
      if (!currentRoom) {
        return;
      }
      window.location.href = inviteSmsHref(currentInviteCode());
    });
  }

  if (shareInviteButton) {
    shareInviteButton.addEventListener("click", async () => {
      if (!currentRoom) {
        return;
      }
      const inviteUrl = inviteUrlForRoom(currentInviteCode());
      const shareData = {
        title: "Bunny AI",
        text: `Join my Bunny private invite: ${inviteUrl}`,
        url: inviteUrl,
      };
      if (navigator.share) {
        await navigator.share(shareData);
        return;
      }
      await navigator.clipboard.writeText(inviteUrl);
      setSetupStatus(translateUi("inviteCopied"));
    });
  }

  startButton.addEventListener("click", () => {
    const action = mediaStream ? stopStreaming() : startStreaming();
    action.catch((error) => {
      micStatusEl.textContent = error.message;
      micStatusState = { key: "", vars: {}, raw: error.message };
      startButton.disabled = false;
    });
  });

  stopButton.addEventListener("click", () => {
    stopStreaming().catch((error) => {
      micStatusEl.textContent = error.message;
      micStatusState = { key: "", vars: {}, raw: error.message };
    });
  });

  sendTextTurnButton.addEventListener("click", () => {
    submitTextTurn().catch((error) => {
      textStatusEl.textContent = error.message;
      renderTextComposer();
    });
  });

  if (sendAttachmentButton) {
    sendAttachmentButton.addEventListener("click", () => {
      if (sendAttachmentButton.disabled || !attachmentInput) {
        return;
      }
      attachmentInput.click();
    });
  }

  emojiPickerButton?.addEventListener("click", () => {
    if (emojiPickerButton.disabled) {
      return;
    }
    if (emojiPickerOpen) {
      closeEmojiPicker();
      return;
    }
    openEmojiPicker();
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Node)) {
      return;
    }
    if (emojiPickerPanel?.contains(event.target) || emojiPickerButton?.contains(event.target)) {
      return;
    }
    closeEmojiPicker();
  });

  if (attachmentInput) {
    attachmentInput.addEventListener("change", () => {
      const [file] = attachmentInput.files || [];
      if (!file) {
        return;
      }
      submitAttachmentTurn(file).catch((error) => {
        textStatusEl.textContent = error.message;
        textStatusEl.hidden = false;
        renderTextComposer();
      });
    });
  }

  textTurnInput.addEventListener("input", () => {
    renderTextComposer();
  });

  textTurnInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && emojiPickerOpen) {
      closeEmojiPicker();
      return;
    }
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }
    event.preventDefault();
    if (!sendTextTurnButton.disabled) {
      submitTextTurn().catch((error) => {
        textStatusEl.textContent = error.message;
        renderTextComposer();
      });
    }
  });
}

function publicAppUrl() {
  return new URL("/", window.location.origin).toString();
}

function hydrateSetupFields() {
  resetSetupFields();
}

function persistSetupFields() {
  // Inputs are intentionally cleared on each page load.
}

function resetSetupFields() {
  localStorage.removeItem(STORAGE_KEY);
  roomCodeInput.value = "";
  if (languageSelect) {
    languageSelect.value = "";
  }
  roomPreviewState = null;
  suggestedRoomId = "";
  textTurnInput.value = "";
  textTurnSubmitting = false;
  attachmentTurnSubmitting = false;
  if (attachmentInput) {
    attachmentInput.value = "";
  }
  roomSessionReady = false;
  setSetupStatus("");
  setMicStatus("micJoinFirst");
  syncProfileIntoSetup();
  renderTextComposer();
  updateTurnGuide();
}

function currentRoomIdDatePrefix() {
  const now = new Date();
  const day = String(now.getDate()).padStart(2, "0");
  const month = String(now.getMonth() + 1).padStart(2, "0");
  return `${day}/${month}`;
}

function nextSuggestedRoomId() {
  return "";
}

function rememberRoomIdSequence(roomId) {
  void roomId;
}

function roomIdToApi(roomId) {
  const trimmed = roomId.trim();
  const normalized = trimmed.toUpperCase();
  const match = normalized.match(/^ID:(\d{2})[/-](\d{2})-(\d{3})$/);
  if (!match) {
    return trimmed;
  }
  return `ID:${match[1]}-${match[2]}-${match[3]}`;
}

function roomIdToDisplay(roomId) {
  const trimmed = roomId.trim();
  const normalized = trimmed.toUpperCase();
  const match = normalized.match(/^ID:(\d{2})-(\d{2})-(\d{3})$/);
  if (!match) {
    return trimmed;
  }
  return `ID:${match[1]}/${match[2]}-${match[3]}`;
}

function ensureDefaultRoomCode() {
  return;
}

function advanceRoomCodeAfterConflict(roomId) {
  void roomId;
  return "";
}

function hydrateRoomCodeFromQuery() {
  const inviteCode = inviteCodeFromQuery();
  if (!inviteCode) {
    return;
  }
  roomCodeInput.value = inviteCode;
  suggestedRoomId = "";
  void refreshRoomPreview(inviteCode);
}

function inferInviteLanguage(room) {
  const activeLanguages = (room?.participants || [])
    .map((participant) => participant.language)
    .filter((language) => language === "ko" || language === "es");
  if (activeLanguages.length === 1) {
    return activeLanguages[0] === "ko" ? "es" : "ko";
  }
  return languageSelect.value || "es";
}

function guestDisplayNameIndex(displayName) {
  const normalized = String(displayName || "").trim();
  if (!normalized.startsWith("Guest")) {
    return null;
  }
  const suffix = normalized.slice("Guest".length).trim();
  if (!suffix) {
    return 1;
  }
  if (/^\d+$/.test(suffix)) {
    return Math.max(Number.parseInt(suffix, 10), 1);
  }
  return null;
}

function nextGuestDisplayName(participants = []) {
  let highestIndex = 0;
  participants.forEach((participant) => {
    if (participant?.user_id != null) {
      return;
    }
    const guestIndex = guestDisplayNameIndex(participant.display_name);
    if (guestIndex != null) {
      highestIndex = Math.max(highestIndex, guestIndex);
    }
  });
  return `Guest${highestIndex + 1}`;
}

async function maybeAutoEnterInvitedRoom() {
  if (!currentUser) {
    return false;
  }
  const inviteCode = inviteCodeFromQuery();
  if (!inviteCode || currentRoom?.invite_code === inviteCode) {
    return false;
  }
  try {
    const room = await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}`);
    const requestedRoomId = roomIdFromQuery();
    if (requestedRoomId && room.room_id && room.room_id !== requestedRoomId) {
      throw new Error("This invite link does not match the room.");
    }
    roomCodeInput.value = inviteCode;
    if (!languageSelect.value) {
      languageSelect.value = inferInviteLanguage(room);
    }
    await joinRoom({ inviteCodeOverride: inviteCode, autoInvite: true });
    return true;
  } catch (error) {
    setSetupStatus(error.message);
    showMyPageScreen();
    return false;
  }
}

async function continueAsGuest() {
  const inviteCode = inviteCodeFromQuery();
  if (!inviteCode) {
    throw new Error("Invite link is missing a private invite code.");
  }
  const room = await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}`);
  const guestLanguage = inferInviteLanguage(room);
  const guestDisplayName = nextGuestDisplayName(room.participants || []);
  currentGuest = {
    display_name: guestDisplayName,
    icon: GUEST_ICON_ID,
    preferred_language: guestLanguage,
  };
  roomCodeInput.value = inviteCode;
  syncProfileIntoSetup();
  languageSelect.value = guestLanguage;
  renderAuthState();
  showMyPageScreen();
  setSetupStatus("Opening your private invite...");
  const joinedRoom = await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}/join`, {
    method: "POST",
    body: JSON.stringify({
      display_name: guestDisplayName,
      icon: GUEST_ICON_ID,
      language: guestLanguage,
    }),
  });
  const participant = joinedRoom.participants[joinedRoom.participants.length - 1];
  currentGuest = {
    display_name: participant?.display_name || guestDisplayName,
    icon: participant?.icon || GUEST_ICON_ID,
    preferred_language: participant?.language || guestLanguage,
  };
  await activateRoom(joinedRoom, participant, false);
}

function audioContextConstructor() {
  return window.AudioContext || window.webkitAudioContext || null;
}

function apiUrl(path) {
  return `${window.location.origin}${path}`;
}

async function requestJson(path, init) {
  const headers = { ...(init?.headers || {}) };
  if (!(init?.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(apiUrl(path), {
    headers,
    ...init,
  });

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep fallback message.
    }
    throw new Error(message);
  }

  return response.json();
}

function inviteUrlForRoom(inviteCode, roomId = currentRoom?.room_id || "") {
  const url = new URL(window.location.href);
  url.searchParams.set("invite", inviteCode);
  if (roomId) {
    url.searchParams.set("room", roomId);
  } else {
    url.searchParams.delete("room");
  }
  return url.toString();
}

function inviteEmailSubject() {
  return translateUi("inviteEmailSubject");
}

function inviteEmailBody(inviteCode) {
  return decodeURIComponent(
    translateUi("inviteEmailBody", {
      url: encodeURIComponent(inviteUrlForRoom(inviteCode)),
    }),
  );
}

function inviteSmsBody(inviteCode) {
  return translateUi("inviteSmsBody", {
    url: inviteUrlForRoom(inviteCode),
  });
}

function inviteEmailHref(inviteCode) {
  const subject = encodeURIComponent(inviteEmailSubject());
  const body = encodeURIComponent(inviteEmailBody(inviteCode));
  return `mailto:?subject=${subject}&body=${body}`;
}

function inviteSmsHref(inviteCode) {
  const body = encodeURIComponent(inviteSmsBody(inviteCode));
  return `sms:?&body=${body}`;
}

function languageLabel(language) {
  if (language === "ko") {
    return "한국어";
  }
  if (language === "es") {
    return "Español";
  }
  return "Auto";
}

function languageIcon(language) {
  if (language === "ko") {
    return "🇰🇷";
  }
  if (language === "es") {
    return "🇲🇽";
  }
  return "🎙️";
}

function createSpeakerVisualElement({ icon = "", language = "auto", className = "speaker-icon" } = {}) {
  const element = document.createElement("span");
  element.className = className;
  applySpeakerVisual(element, icon, language);
  return element;
}

function counterpartLanguage(sourceLanguage) {
  return sourceLanguage === "ko" ? "es" : "ko";
}

function roomCreatorParticipantId() {
  return currentRoom?.creator_participant_id || null;
}

function participantRole(participantId) {
  if (!participantId) {
    return "Speaker";
  }
  const creatorId = roomCreatorParticipantId();
  if (!creatorId) {
    return "Speaker";
  }
  return participantId === creatorId ? "Host" : "Guest";
}

function participantLaneClass(participantId) {
  const creatorId = roomCreatorParticipantId();
  if (!creatorId) {
    return "creator";
  }
  return participantId === creatorId ? "creator" : "guest";
}

function micLabels() {
  return {
    start: translateUi("speak"),
    stop: translateUi("stop"),
  };
}

function currentUiLanguage() {
  const language = selfParticipant?.language || languageSelect.value;
  if (language === "ko" || language === "es") {
    return language;
  }
  return "en";
}

function translateUi(key, vars = {}) {
  const locale = UI_COPY[currentUiLanguage()] || UI_COPY.en;
  const fallback = UI_COPY.en[key] || "";
  const template = locale[key] || fallback;
  return template.replace(/\{(\w+)\}/g, (_, token) => `${vars[token] ?? ""}`);
}

function closeEmojiPicker() {
  emojiPickerOpen = false;
  if (emojiPickerPanel) {
    emojiPickerPanel.hidden = true;
  }
  emojiPickerButton?.setAttribute("aria-expanded", "false");
}

function openEmojiPicker() {
  emojiPickerOpen = true;
  renderEmojiPicker();
  if (emojiPickerPanel) {
    emojiPickerPanel.hidden = false;
  }
  emojiPickerButton?.setAttribute("aria-expanded", "true");
}

function insertEmojiIntoComposer(emoji) {
  if (!textTurnInput || textTurnInput.disabled) {
    return;
  }
  const start = textTurnInput.selectionStart ?? textTurnInput.value.length;
  const end = textTurnInput.selectionEnd ?? start;
  textTurnInput.setRangeText(emoji, start, end, "end");
  textTurnInput.focus();
  renderTextComposer();
}

function renderEmojiPicker() {
  if (!emojiPickerPanel || !emojiPickerGrid) {
    return;
  }
  emojiPickerGrid.innerHTML = "";

  EMOJI_SETS.forEach((set) => {
    set.items.forEach((emoji) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "emoji-picker__item";
      button.textContent = emoji;
      button.setAttribute("aria-label", emoji);
      button.addEventListener("click", () => {
        insertEmojiIntoComposer(emoji);
      });
      emojiPickerGrid.appendChild(button);
    });
  });
}

function setMicStatus(key, vars = {}) {
  micStatusState = { key, vars, raw: "" };
  micStatusEl.textContent = translateUi(key, vars);
}

function rerenderMicStatus() {
  if (micStatusState.raw) {
    micStatusEl.textContent = micStatusState.raw;
    return;
  }
  if (!micStatusState.key) {
    micStatusEl.textContent = "";
    return;
  }
  micStatusEl.textContent = translateUi(micStatusState.key, micStatusState.vars);
}

function rerenderLanguageDependentCopy() {
  renderAppShareRow();
  renderHostStatusDot();
  renderMicButtons();
  rerenderMicStatus();
  renderInviteCard();
  renderTextComposer();
  updateTurnGuide();
}

function renderAppShareRow() {
  if (!shareAppButton) {
    return;
  }
  shareAppButton.textContent = "Invite";
  shareAppButton.disabled = !currentUser || !currentRoom;
  if (chatInviteButton) {
    chatInviteButton.textContent = translateUi("inviteButton");
    chatInviteButton.disabled = !currentRoom;
  }
}

function renderHostStatusDot() {
  if (!hostStatusDotEl || !hostStatusTextEl) {
    return;
  }

  hostStatusDotEl.classList.remove(
    "host-status-dot--checking",
    "host-status-dot--online",
    "host-status-dot--offline",
  );

  if (serviceAvailability.online == null) {
    hostStatusDotEl.classList.add("host-status-dot--checking");
    hostStatusDotEl.setAttribute("aria-label", "Checking host status");
    hostStatusDotEl.title = "Checking host status";
    hostStatusTextEl.textContent = translateUi("hostStatusChecking");
    return;
  }

  if (serviceAvailability.online) {
    hostStatusDotEl.classList.add("host-status-dot--online");
    hostStatusDotEl.setAttribute("aria-label", "Bunny host online");
    hostStatusDotEl.title = "Bunny host online";
    hostStatusTextEl.textContent = translateUi("hostStatusOnline");
    return;
  }

  hostStatusDotEl.classList.add("host-status-dot--offline");
  hostStatusDotEl.setAttribute("aria-label", "Bunny host offline");
  hostStatusDotEl.title = "Bunny host offline";
  hostStatusTextEl.textContent = translateUi("hostStatusOffline");
}

function startRuntimePolling() {
  if (runtimePollIntervalId) {
    window.clearInterval(runtimePollIntervalId);
  }
  runtimePollIntervalId = window.setInterval(() => {
    void refreshRuntimeReadiness({ silent: true });
  }, RUNTIME_POLL_INTERVAL_MS);
}

function renderInviteCard() {
  if (!inviteCardEl) {
    return;
  }
  const hasRoom = Boolean(currentRoom);
  inviteCardEl.hidden = !hasRoom;
  inviteCardTitleEl.textContent = translateUi("inviteTitle");
  inviteCardBodyEl.textContent = translateUi("inviteBody");
  emailInviteButton.textContent = translateUi("inviteEmail");
  smsInviteButton.textContent = translateUi("inviteSms");
  shareInviteButton.textContent = translateUi("inviteShare");
  copyInviteButton.textContent = translateUi("inviteCopy");
  if (!hasRoom) {
    inviteRoomCodeButton.textContent = translateUi("inviteRoomCode");
    inviteLinkAnchorEl.textContent = translateUi("inviteOpenLink");
    inviteLinkAnchorEl.removeAttribute("href");
    inviteRoomCodeButton.disabled = true;
    copyInviteButton.disabled = true;
    emailInviteButton.disabled = true;
    smsInviteButton.disabled = true;
    shareInviteButton.disabled = true;
    return;
  }
  const inviteUrl = inviteUrlForRoom(currentInviteCode());
  inviteRoomCodeButton.textContent = translateUi("inviteRoomCode");
  inviteLinkAnchorEl.textContent = translateUi("inviteOpenLink");
  inviteLinkAnchorEl.href = inviteUrl;
  inviteRoomCodeButton.disabled = false;
  copyInviteButton.disabled = false;
  emailInviteButton.disabled = false;
  smsInviteButton.disabled = false;
  shareInviteButton.disabled = false;
}

function renderMicButtons() {
  const labels = micLabels();
  const micIsLive = Boolean(mediaStream);
  startButton.textContent = "";
  startButton.classList.toggle("is-live", micIsLive);
  startButton.setAttribute("aria-label", micIsLive ? labels.stop : labels.start);
  startButton.setAttribute("title", micIsLive ? labels.stop : labels.start);
  startButton.setAttribute("data-tooltip", micIsLive ? labels.stop : labels.start);
  stopButton.hidden = true;
  stopButton.disabled = true;
  if (exitRoomButton) {
    exitRoomButton.textContent = "";
    exitRoomButton.setAttribute("aria-label", translateUi("exitButton"));
    exitRoomButton.setAttribute("title", translateUi("exitButton"));
    exitRoomButton.setAttribute("data-tooltip", translateUi("exitButton"));
  }
  if (homeRoomButton) {
    homeRoomButton.textContent = "";
    homeRoomButton.setAttribute("aria-label", "Home");
    homeRoomButton.setAttribute("title", "Home");
    homeRoomButton.setAttribute("data-tooltip", "Home");
    homeRoomButton.disabled = !currentUser;
  }
  if (chatInviteButton) {
    chatInviteButton.textContent = "";
    chatInviteButton.setAttribute("aria-label", translateUi("inviteTitle"));
    chatInviteButton.setAttribute("title", translateUi("inviteTitle"));
    chatInviteButton.setAttribute("data-tooltip", translateUi("inviteTitle"));
  }
  syncScreenActionButtons();
}

function renderTextComposer() {
  const hasRoom = Boolean(currentRoom && selfParticipant);
  const hasText = Boolean(textTurnInput.value.trim());
  const isBusy = textTurnSubmitting || attachmentTurnSubmitting;
  textShellEl.hidden = false;
  textShellTitleEl.textContent = "";
  textShellTitleEl.hidden = true;
  textTurnInput.placeholder = translateUi("textPlaceholder");
  textTurnInput.disabled = !hasRoom || isBusy;
  if (sendAttachmentButton) {
    sendAttachmentButton.textContent = "";
    sendAttachmentButton.setAttribute("aria-label", translateUi("fileButton"));
    sendAttachmentButton.setAttribute("title", translateUi("fileButton"));
    sendAttachmentButton.setAttribute("data-tooltip", translateUi("fileButton"));
    sendAttachmentButton.disabled = !hasRoom || isBusy;
  }
  if (emojiPickerButton) {
    emojiPickerButton.textContent = "";
    emojiPickerButton.setAttribute("aria-label", translateUi("emojiButton"));
    emojiPickerButton.setAttribute("title", translateUi("emojiButton"));
    emojiPickerButton.setAttribute("data-tooltip", translateUi("emojiButton"));
    emojiPickerButton.disabled = !hasRoom || isBusy;
  }
  sendTextTurnButton.textContent = "";
  sendTextTurnButton.setAttribute("aria-label", translateUi("sendButton"));
  sendTextTurnButton.setAttribute("title", translateUi("sendButton"));
  sendTextTurnButton.setAttribute("data-tooltip", translateUi("sendButton"));
  sendTextTurnButton.disabled = !hasRoom || isBusy || !hasText;

  if (!hasRoom) {
    closeEmojiPicker();
    textStatusEl.textContent = translateUi("textJoinFirstExtended");
    textStatusEl.hidden = false;
    return;
  }

  if (textTurnSubmitting) {
    textStatusEl.textContent = translateUi("textSending");
    textStatusEl.hidden = false;
    return;
  }

  if (attachmentTurnSubmitting) {
    closeEmojiPicker();
    textStatusEl.textContent = translateUi("textUploadingFile");
    textStatusEl.hidden = false;
    return;
  }

  textStatusEl.textContent = "";
  textStatusEl.hidden = true;
  if (emojiPickerOpen) {
    renderEmojiPicker();
  }
}

function isBrowserMicReady() {
  return Boolean(navigator.mediaDevices?.getUserMedia && audioContextConstructor());
}

function renderBadgeRow(container, badges) {
  container.innerHTML = "";
  badges.forEach((badge) => {
    const chip = document.createElement("span");
    chip.className = `badge${badge.tone ? ` badge--${badge.tone}` : ""}`;
    chip.textContent = badge.label;
    container.appendChild(chip);
  });
}

function renderRuntimeUnavailable(message) {
  renderBadgeRow(asrReadinessEl, [{ label: "Backend unavailable", tone: "error" }]);
  renderBadgeRow(translationReadinessEl, [{ label: "Backend unavailable", tone: "error" }]);
  renderBadgeRow(browserReadinessEl, [
    {
      label: isBrowserMicReady() ? "Microphone supported" : "Microphone unsupported",
      tone: isBrowserMicReady() ? "ready" : "error",
    },
  ]);
  demoReadinessEl.textContent = message;
  serviceAvailability = { online: false, errorMessage: "" };
  renderHostStatusDot();
}

function renderInvitePreview({
  hidden = true,
  tone = "neutral",
  label = "Waiting",
  title = "Open an invite link to preview the room.",
  body = "When a private invite link is present, this panel will show who is already inside and which side is available next.",
} = {}) {
  invitePreviewEl.hidden = hidden;
  invitePreviewBadgeEl.className = `signal-badge signal-badge--${tone}`;
  invitePreviewBadgeEl.textContent = label;
  invitePreviewTitleEl.textContent = title;
  invitePreviewBodyEl.textContent = body;
}

async function refreshRoomPreview(inviteCode) {
  const requestId = (roomPreviewRequestId += 1);

  renderInvitePreview({
    hidden: false,
    tone: "neutral",
    label: "Checking",
    title: "Checking your private invite",
    body: "Checking who is already inside before you join this room.",
  });

  try {
    const room = await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}`);
    if (requestId !== roomPreviewRequestId) {
      return;
    }
    roomPreviewState = room;

    const participantSummary = room.participants.length
      ? room.participants
          .map((participant) => `${participant.display_name} (${languageLabel(participant.language)})`)
          .join(", ")
      : "No participants yet";

    if (room.participant_count >= 2) {
      renderInvitePreview({
        hidden: false,
        tone: "warning",
        label: "Full",
        title: "This private room already has two speakers",
        body: `${participantSummary}. Open a different invite link or create a new room.`,
      });
      return;
    }

    renderInvitePreview({
      hidden: false,
      tone: "ready",
      label: "Ready",
      title: `${participantSummary} is already inside`,
      body: "Choose your language, enter your name, and continue with this private invite.",
    });
  } catch (error) {
    if (requestId !== roomPreviewRequestId) {
      return;
    }
    roomPreviewState = null;
    renderInvitePreview({
      hidden: false,
      tone: "error",
      label: "Missing",
      title: "This private invite could not be loaded",
      body: error.message || "Check the invite link or create a new room instead.",
    });
  }
}

function buildRuntimeBadge(status, label) {
  if (!status) {
    return { label: `${label} unavailable`, tone: "error" };
  }
  if (!status.ready) {
    return { label: `${label} not ready`, tone: "error" };
  }
  if (status.engine === "mock") {
    return { label: `${label} mock`, tone: "warning" };
  }
  return { label: `${label} ${status.engine}`, tone: "ready" };
}

function runtimeReadyForLiveSpeech(payload) {
  return Boolean(
    payload?.asr?.ready &&
      payload?.translation?.ready &&
      payload.asr.engine !== "mock" &&
      payload.translation.engine !== "mock",
  );
}

function renderRuntimeReadiness(payload) {
  renderBadgeRow(asrReadinessEl, [buildRuntimeBadge(payload.asr, "ASR")]);
  renderBadgeRow(translationReadinessEl, [buildRuntimeBadge(payload.translation, "Translation")]);
  renderBadgeRow(browserReadinessEl, [
    {
      label: isBrowserMicReady() ? "Microphone supported" : "Microphone unsupported",
      tone: isBrowserMicReady() ? "ready" : "error",
    },
  ]);

  serviceAvailability = { online: true, errorMessage: "" };
  roomCapacity = payload?.room_store?.max_participants || roomCapacity;
  renderHostStatusDot();

  if (runtimeReadyForLiveSpeech(payload)) {
    demoReadinessEl.textContent =
      "Realtime speech demo ready. Open this page on two devices, join the same room, and let each speaker take turns.";
    return;
  }

  if (payload?.asr?.engine === "mock" || payload?.translation?.engine === "mock") {
    demoReadinessEl.textContent =
      "This backend is still using mock runtime. Use scripts/run_real_demo.sh or .env.real-demo.example before attempting a real two-user speech demo.";
    return;
  }

  demoReadinessEl.textContent =
    "The backend is reachable but the speech runtime is not fully ready. Check model paths and engine readiness in /healthz.";
}

async function refreshRuntimeReadiness({ silent = false } = {}) {
  try {
    const payload = await requestJson("/healthz");
    renderRuntimeReadiness(payload);
    return payload;
  } catch (error) {
    renderRuntimeUnavailable(
      "Unable to reach Bunny on the host Mac right now. Ask the host to open Bunny Public Start.app and then refresh.",
    );
    if (!silent) {
      throw error;
    }
    return null;
  }
}

function inferSourceLanguage(sourceLanguage, sourceText, translations) {
  if (sourceLanguage === "ko" || sourceLanguage === "es") {
    return sourceLanguage;
  }
  if (translations?.ko === sourceText) {
    return "ko";
  }
  if (translations?.es === sourceText) {
    return "es";
  }
  return /[가-힣]/.test(sourceText) ? "ko" : "es";
}

function isNonverbalText(text) {
  const stripped = String(text || "").trim();
  if (!stripped) {
    return false;
  }
  const hasWordLike = Array.from(stripped).some((char) => {
    if (/\d/.test(char) || /[A-Za-z]/.test(char) || /[가-힣]/.test(char)) {
      return true;
    }
    return char.toLowerCase() !== char.toUpperCase();
  });
  if (hasWordLike) {
    return false;
  }
  return Array.from(stripped).some((char) => !/\s/.test(char));
}

function baseRoomTitle(displayName) {
  const ownerName = String(displayName || "").trim() || "User";
  return `${ownerName}'s Room`;
}

function escapeRegExp(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function readRoomTitleSequenceMap() {
  try {
    const raw = localStorage.getItem(ROOM_ID_SEQUENCE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function writeRoomTitleSequenceMap(nextMap) {
  try {
    localStorage.setItem(ROOM_ID_SEQUENCE_KEY, JSON.stringify(nextMap));
  } catch (_error) {
    // Ignore storage failures and keep generating titles in memory for this session.
  }
}

function nextAutoRoomTitle(displayName) {
  const ownerName = String(displayName || "").trim() || "User";
  const baseTitle = baseRoomTitle(ownerName);
  const titlePattern = new RegExp(`^${escapeRegExp(baseTitle)} (\\d{2,})$`);
  const historyMax = roomHistory.reduce((max, room) => {
    const match = room?.room_title?.trim().match(titlePattern);
    if (!match) {
      return max;
    }
    return Math.max(max, Number.parseInt(match[1], 10) || 0);
  }, 0);
  const storedSequences = readRoomTitleSequenceMap();
  const storedMax = Number.isFinite(storedSequences[ownerName]) ? storedSequences[ownerName] : 0;
  const nextSequence = Math.max(historyMax, storedMax) + 1;
  storedSequences[ownerName] = nextSequence;
  writeRoomTitleSequenceMap(storedSequences);
  return `${baseTitle} ${String(nextSequence).padStart(2, "0")}`;
}

function fallbackRoomTitle() {
  return baseRoomTitle(
    selfParticipant?.display_name?.trim() ||
      currentUser?.display_name?.trim() ||
      currentGuest?.display_name?.trim() ||
      "User",
  );
}

function renderRoomHeader() {
  roomTitleEl.textContent = "";
  if (chatRoomTitleInput) {
    if (!currentRoom) {
      chatRoomTitleInput.value = "";
      chatRoomTitleInput.disabled = true;
      chatRoomTitleInput.hidden = true;
      if (chatRoomTitleDisplay) {
        chatRoomTitleDisplay.hidden = false;
      }
      if (chatRoomTitleText) {
        chatRoomTitleText.textContent = fallbackRoomTitle();
      }
      chatRoomTitleDisplay?.classList.add("room-settings-bar__title-display--placeholder");
      if (chatRoomTitleEditButton) {
        chatRoomTitleEditButton.hidden = true;
      }
    } else {
      const savedTitle = (currentRoom.title || "").trim();
      const visibleTitle = savedTitle || fallbackRoomTitle();
      const shouldEdit = roomTitleEditing;
      if (document.activeElement !== chatRoomTitleInput) {
        chatRoomTitleInput.value = savedTitle;
      }
      chatRoomTitleInput.disabled = false;
      chatRoomTitleInput.hidden = !shouldEdit;
      if (chatRoomTitleDisplay && chatRoomTitleText) {
        chatRoomTitleText.textContent = visibleTitle;
        chatRoomTitleDisplay.hidden = shouldEdit;
        chatRoomTitleDisplay.classList.toggle("room-settings-bar__title-display--placeholder", !savedTitle);
      }
      if (chatRoomTitleEditButton) {
        chatRoomTitleEditButton.hidden = false;
        const titleActionLabel = shouldEdit ? "Save" : "Edit";
        chatRoomTitleEditButton.setAttribute("aria-label", titleActionLabel);
        chatRoomTitleEditButton.setAttribute("title", titleActionLabel);
        chatRoomTitleEditButton.setAttribute("data-tooltip", titleActionLabel);
        chatRoomTitleEditButton.setAttribute("data-mode", shouldEdit ? "save" : "edit");
      }
    }
  }
  if (chatLanguageSelect) {
    chatLanguageSelect.value = selfParticipant?.language || currentUser?.preferred_language || "";
    chatLanguageSelect.disabled = !currentRoom || !selfParticipant;
  }
  const socketReady = Boolean(socket && socket.readyState === WebSocket.OPEN && roomSessionReady);
  const otherSpeakerIsActive =
    activeSpeaker &&
    activeSpeaker.active &&
    activeSpeaker.participantId !== selfParticipant?.participant_id;
  startButton.disabled = !socketReady || !selfParticipant || (!mediaStream && otherSpeakerIsActive);
  stopButton.disabled = !mediaStream;
  syncScreenActionButtons();
}

function setTurnGuide(title, body) {
  turnGuideTitleEl.textContent = title;
  turnGuideBodyEl.textContent = body;
}

function clearReconnectTimer() {
  if (reconnectTimeoutId) {
    window.clearTimeout(reconnectTimeoutId);
    reconnectTimeoutId = null;
  }
}

function updateTurnGuide() {
  if (!currentRoom || !selfParticipant) {
    setTurnGuide(
      translateUi("turnWaitingTitle"),
      translateUi("turnWaitingBody"),
    );
    return;
  }

  if (!socket) {
    setTurnGuide(
      translateUi("turnReconnectTitle"),
      reconnectAttempt > 0
        ? translateUi("turnReconnectBodyAttempt", { attempt: reconnectAttempt })
        : translateUi("turnReconnectBodyIdle"),
    );
    return;
  }

  if (mediaStream) {
    setTurnGuide(
      translateUi("turnSpeakingTitle"),
      translateUi("turnSpeakingBody"),
    );
    return;
  }

  if (activeSpeaker?.active) {
    const isSelf = activeSpeaker.participantId === selfParticipant.participant_id;
    if (isSelf) {
      setTurnGuide(
        translateUi("turnStartingTitle"),
        translateUi("turnStartingBody"),
      );
      return;
    }
    setTurnGuide(
      translateUi("turnPartnerSpeakingTitle", { name: activeSpeaker.displayName }),
      translateUi("turnPartnerSpeakingBody", { name: activeSpeaker.displayName }),
    );
    return;
  }

  const partner = currentRoom.participants.find(
    (participant) => participant.participant_id !== selfParticipant.participant_id,
  );
  if (!partner) {
    setTurnGuide(
      translateUi("turnWaitingPartnerTitle"),
      translateUi("turnWaitingPartnerBody"),
    );
    return;
  }

  setTurnGuide(
    translateUi("turnYourTurnTitle"),
    translateUi("turnYourTurnBody", {
      language: languageLabel(selfParticipant.language),
      name: partner.display_name,
    }),
  );
}

function renderParticipants(participants) {
  if (!participantListEl) {
    return;
  }
  participantListEl.innerHTML = "";
  if (!participants.length) {
    const placeholder = document.createElement("article");
    placeholder.className = "participant-empty";
    placeholder.textContent = "Participants will appear here after joining a room.";
    participantListEl.appendChild(placeholder);
    return;
  }

  participants.forEach((participant) => {
    const article = document.createElement("article");
    article.className = "participant-card";
    const avatar = createSpeakerVisualElement({
      icon: participant.icon || "",
      language: participant.language,
      className: "participant-card__avatar",
    });
    const copy = document.createElement("div");
    copy.className = "participant-card__copy";
    copy.innerHTML = `
      <div class="participant-name">${escapeHtml(participant.display_name)}</div>
      <div class="participant-meta">${languageLabel(participant.language)}</div>
    `;
    article.append(avatar, copy);
    participantListEl.appendChild(article);
  });
}

function clearConversation() {
  conversationEl.innerHTML = "";
  conversationEl.hidden = true;
  appendedTurnIds = new Set();
  lastAppendedTurnSignature = null;
  lastAppendedTurnAt = 0;
  conversationTurnCounter = 0;
  if (emptyStateEl) {
    conversationEl.appendChild(emptyStateEl);
  }
}

function hideLiveCaption() {
  liveTurnState = null;
  liveCaptionEl.hidden = true;
  liveCaptionEl.classList.remove("live-caption--creator", "live-caption--guest");
  liveCaptionMetaEl.textContent = "";
  liveSourceTextEl.textContent = "";
  liveTranslatedTextEl.textContent = "";
}

function createLatencyProbe() {
  return {
    turnActiveAt: 0,
    firstSourceSeenAt: 0,
    firstTranslationShownAt: 0,
  };
}

function resetLatencyProbe({ turnActive = false } = {}) {
  latencyProbe = createLatencyProbe();
  if (turnActive) {
    latencyProbe.turnActiveAt = performance.now();
  }
}

function noteSourceVisible() {
  if (!latencyProbe.firstSourceSeenAt) {
    latencyProbe.firstSourceSeenAt = performance.now();
  }
}

function noteTranslationVisible() {
  if (!latencyProbe.firstTranslationShownAt) {
    latencyProbe.firstTranslationShownAt = performance.now();
  }
}

function latencyMetricParts() {
  if (!latencyProbe.firstTranslationShownAt) {
    return [];
  }

  const parts = [];
  if (latencyProbe.firstSourceSeenAt) {
    parts.push(
      `first translation ${Math.round(latencyProbe.firstTranslationShownAt - latencyProbe.firstSourceSeenAt)}ms`,
    );
  }
  if (latencyProbe.turnActiveAt) {
    parts.push(
      `turn->translation ${Math.round(latencyProbe.firstTranslationShownAt - latencyProbe.turnActiveAt)}ms`,
    );
  }
  return parts;
}

function formatClockTime(timestampMs) {
  if (!timestampMs) {
    return "";
  }
  return new Date(timestampMs).toLocaleTimeString("ko-KR", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function renderTimedSentence(text, timestampMs) {
  const escapedText = escapeHtml(text.trim());
  const clockTime = formatClockTime(timestampMs);
  if (!clockTime) {
    return `<span class="turn-text__body">${escapedText}</span>`;
  }
  return `<span class="turn-text__body">${escapedText}</span><span class="turn-time">${escapeHtml(clockTime)}</span>`;
}

function updateLiveCaption({
  speakerName,
  speakerParticipantId,
  sourceLanguage,
  sourceText,
  translatedText = "",
  sourceShownAt = 0,
  translatedShownAt = 0,
}) {
  const trimmed = sourceText.trim();
  if (!trimmed) {
    hideLiveCaption();
    return;
  }
  noteSourceVisible();
  const previousState = liveTurnState;
  const nextSourceShownAt = sourceShownAt || previousState?.sourceShownAt || Date.now();
  let nextTranslatedShownAt = translatedShownAt || previousState?.translatedShownAt || 0;
  if (translatedText?.trim()) {
    noteTranslationVisible();
    nextTranslatedShownAt ||= Date.now();
  }

  liveTurnState = {
    speakerName,
    speakerParticipantId,
    sourceLanguage,
    sourceText: trimmed,
    translatedText,
    sourceShownAt: nextSourceShownAt,
    translatedShownAt: nextTranslatedShownAt,
  };
  renderLiveCaption();
}

function renderLiveCaption() {
  if (!liveTurnState || !liveTurnState.sourceText.trim()) {
    hideLiveCaption();
    return;
  }

  const {
    speakerName,
    speakerParticipantId,
    sourceLanguage,
    sourceText,
    translatedText,
    sourceShownAt,
    translatedShownAt,
  } = liveTurnState;
  const targetLanguage = counterpartLanguage(sourceLanguage);
  const laneClass = participantLaneClass(speakerParticipantId);
  const isSelfSpeaker = Boolean(selfParticipant && speakerParticipantId === selfParticipant.participant_id);
  liveCaptionEl.classList.remove("live-caption--creator", "live-caption--guest", "live-caption--self");
  liveCaptionEl.classList.add(`live-caption--${laneClass}`);
  if (isSelfSpeaker) {
    liveCaptionEl.classList.add("live-caption--self");
  }
  liveCaptionEl.hidden = false;
  liveCaptionMetaEl.textContent = `${speakerName} · ${languageLabel(sourceLanguage)}`;
  liveSourceTextEl.innerHTML = renderTimedSentence(sourceText, sourceShownAt);
  liveTranslatedTextEl.innerHTML = translatedText?.trim()
    ? renderTimedSentence(translatedText.trim(), translatedShownAt)
    : isNonverbalText(sourceText)
      ? ""
      : "Translation pending...";
}

function appendConversationTurn({
  turnId = "",
  speakerName,
  speakerParticipantId,
  speakerIcon = "",
  sourceLanguage,
  sourceText,
  translatedText,
  sourceShownAt = 0,
  translatedShownAt = 0,
}) {
  if (turnId && appendedTurnIds.has(turnId)) {
    return;
  }

  const signature = [
    speakerParticipantId,
    sourceLanguage,
    sourceText.trim(),
    translatedText.trim(),
  ].join("::");
  const now = Date.now();
  if (signature === lastAppendedTurnSignature && now - lastAppendedTurnAt < 4000) {
    return;
  }

  const empty = conversationEl.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
  conversationEl.hidden = false;

  conversationEl.querySelectorAll(".turn--latest").forEach((turn) => {
    turn.classList.remove("turn--latest");
  });

  conversationTurnCounter += 1;

  const creatorId = roomCreatorParticipantId();
  const speakerIsCreator = creatorId ? speakerParticipantId === creatorId : true;
  const isSelfSpeaker = Boolean(selfParticipant && speakerParticipantId === selfParticipant.participant_id);
  const showTranslation = Boolean(
    translatedText.trim() && !(isNonverbalText(sourceText) && translatedText.trim() === sourceText.trim()),
  );
  const article = document.createElement("article");
  article.className = `turn ${isSelfSpeaker ? "turn--creator" : "turn--guest"}${isSelfSpeaker ? " turn--self" : " turn--other"}${speakerIsCreator ? " turn--host" : ""} turn--latest`;
  article.innerHTML = `
    <div class="turn-header">
      <span class="turn-header__meta">${escapeHtml(speakerName)} · ${languageLabel(sourceLanguage)}</span>
    </div>
    <div class="turn-body">
      <div class="turn-copy">
        <p class="turn-text turn-text--source">
          ${renderTimedSentence(sourceText, sourceShownAt)}
        </p>
        ${showTranslation ? `<p class="turn-text turn-text--translation">${renderTimedSentence(translatedText, translatedShownAt)}</p>` : ""}
      </div>
    </div>
  `;
  const turnBody = article.querySelector(".turn-body");
  turnBody?.prepend(
    createSpeakerVisualElement({
      icon: speakerIcon,
      language: sourceLanguage,
    }),
  );

  conversationEl.prepend(article);
  if (turnId) {
    appendedTurnIds.add(turnId);
  }
  lastAppendedTurnSignature = signature;
  lastAppendedTurnAt = now;
  trimConversationHistory();
  conversationEl.scrollTop = 0;
}

function appendSystemConversationTurn(message, timestampMs = Date.now()) {
  if (!conversationEl || !message?.trim()) {
    return;
  }

  const empty = conversationEl.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
  conversationEl.hidden = false;

  conversationEl.querySelectorAll(".turn--latest").forEach((turn) => {
    turn.classList.remove("turn--latest");
  });

  conversationTurnCounter += 1;
  const article = document.createElement("article");
  article.className = "turn turn--system turn--latest";
  article.innerHTML = `
    <div class="turn-header">
      <span class="turn-header__meta">알림 · 시스템</span>
    </div>
    <div class="turn-body turn-body--system">
      <div class="turn-copy turn-copy--system">
        <p class="turn-text turn-text--source turn-text--system">
          ${renderTimedSentence(message, timestampMs)}
        </p>
      </div>
    </div>
  `;

  conversationEl.prepend(article);
  trimConversationHistory();
  conversationEl.scrollTop = 0;
}

function appendAttachmentTurn({
  turnId = "",
  speakerName,
  speakerParticipantId,
  speakerIcon = "",
  sourceLanguage,
  attachment,
  createdAt = 0,
}) {
  if (!attachment?.file_name || !attachment?.file_url) {
    return;
  }
  if (turnId && appendedTurnIds.has(turnId)) {
    return;
  }

  const signature = [
    speakerParticipantId,
    "attachment",
    attachment.file_name,
    attachment.file_url,
  ].join("::");
  const now = Date.now();
  if (signature === lastAppendedTurnSignature && now - lastAppendedTurnAt < 4000) {
    return;
  }

  const empty = conversationEl.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
  conversationEl.hidden = false;
  conversationEl.querySelectorAll(".turn--latest").forEach((turn) => {
    turn.classList.remove("turn--latest");
  });

  conversationTurnCounter += 1;
  const creatorId = roomCreatorParticipantId();
  const speakerIsCreator = creatorId ? speakerParticipantId === creatorId : true;
  const isSelfSpeaker = Boolean(selfParticipant && speakerParticipantId === selfParticipant.participant_id);
  const article = document.createElement("article");
  article.className = `turn ${isSelfSpeaker ? "turn--creator" : "turn--guest"}${isSelfSpeaker ? " turn--self" : " turn--other"}${speakerIsCreator ? " turn--host" : ""} turn--attachment turn--latest`;
  article.innerHTML = `
    <div class="turn-header">
      <span class="turn-header__meta">${escapeHtml(speakerName)} · File</span>
    </div>
    <div class="turn-line turn-line--attachment">
      <div class="turn-attachment__content"></div>
    </div>
  `;
  const attachmentLine = article.querySelector(".turn-line");
  attachmentLine?.prepend(
    createSpeakerVisualElement({
      icon: speakerIcon,
      language: sourceLanguage,
    }),
  );

  const content = article.querySelector(".turn-attachment__content");
  if (content) {
    const link = document.createElement("a");
    link.className = "turn-attachment__link";
    link.href = attachmentHref(attachment);
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = attachment.file_name;

    if (isImageAttachment(attachment)) {
      const image = document.createElement("img");
      image.className = "turn-attachment__image";
      image.src = attachmentHref(attachment);
      image.alt = attachment.file_name;
      content.appendChild(image);
    }

    const meta = document.createElement("p");
    meta.className = "turn-attachment__meta";
    const details = [attachment.content_type || "file", formatFileSize(attachment.size_bytes), createdAt ? new Date(createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : ""].filter(Boolean);
    meta.textContent = details.join(" · ");

    content.appendChild(link);
    content.appendChild(meta);
  }

  conversationEl.prepend(article);
  if (turnId) {
    appendedTurnIds.add(turnId);
  }
  lastAppendedTurnSignature = signature;
  lastAppendedTurnAt = now;
  trimConversationHistory();
  conversationEl.scrollTop = 0;
}

function trimConversationHistory() {
  const turns = conversationEl.querySelectorAll(".turn");
  const overflow = turns.length - MAX_CONVERSATION_TURNS;
  if (overflow <= 0) {
    return;
  }
  for (let index = 0; index < overflow; index += 1) {
    turns[index].remove();
  }
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderMetrics(metrics) {
  const latencyParts = latencyMetricParts();
  if ((!metrics || Object.keys(metrics).length === 0) && latencyParts.length === 0) {
    metricsEl.textContent = "No speech yet";
    return;
  }
  const parts = [];
  if (metrics.audio_seconds != null) {
    parts.push(`audio ${metrics.audio_seconds}s`);
  }
  if (metrics.asr_ms != null) {
    parts.push(`ASR ${metrics.asr_ms}ms`);
  }
  if (metrics.translation_ms != null) {
    parts.push(`translation ${metrics.translation_ms}ms`);
  }
  if (metrics.pipeline_ms != null) {
    parts.push(`pipeline ${metrics.pipeline_ms}ms`);
  }
  parts.push(...latencyParts);
  metricsEl.textContent = parts.join(" | ");
}

async function createRoom(attempt = 0) {
  void attempt;
  if (!currentUser) {
    throw new Error("로그인 후 이용할 수 있습니다.");
  }
  const draft = currentProfileDraft();
  const displayName = draft.display_name;
  const language = draft.preferred_language;
  if (!displayName) {
    throw new Error("Enter your name first.");
  }
  if (!language) {
    throw new Error("Choose your language first.");
  }

  persistSetupFields();
  setSetupStatus("Creating room...");
  const requestedTitle = chatRoomTitleInput?.value.trim() || "";
  const room = await requestJson("/api/rooms", {
    method: "POST",
    body: JSON.stringify({
      display_name: displayName,
      icon: draft.icon,
      title: requestedTitle || nextAutoRoomTitle(displayName),
      language,
    }),
  });

  const participant = room.participants[0];
  roomCodeInput.value = room.invite_code || "";
  renderInvitePreview({
    hidden: false,
    tone: "ready",
    label: "Created",
    title: "Your private room is ready to share",
    body: "Copy the private invite link so the other speaker can choose a language and join this room.",
  });
  await activateRoom(room, participant, true, { openChat: true });
}

async function joinRoom({ inviteCodeOverride = "", autoInvite = false } = {}) {
  const actor = currentActor();
  if (!actor) {
    throw new Error("로그인 또는 Guest 입장 후 이용할 수 있습니다.");
  }
  const draft = currentProfileDraft();
  const displayName = draft.display_name;
  const inviteCode = inviteCodeOverride || inviteCodeFromQuery() || roomCodeInput.value.trim();
  const language = draft.preferred_language;
  if (!displayName) {
    throw new Error("Enter your name first.");
  }
  if (!language) {
    throw new Error("Choose your language first.");
  }
  if (!inviteCode) {
    throw new Error("Open a private invite link first.");
  }
  await ensureRoomCanBeJoined(inviteCode);

  persistSetupFields();
  setSetupStatus(autoInvite ? "Opening your private invite..." : "Joining from private invite...");
  const room = await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}/join`, {
    method: "POST",
    body: JSON.stringify({
      display_name: displayName,
      icon: draft.icon || actor.icon || "",
      language,
    }),
  });

  const knownParticipantId =
    roomHistory.find((item) => item.room_id === room.room_id)?.participant_id || "";
  const participant =
    room.participants.find((item) => item.participant_id === knownParticipantId) ||
    room.participants.find(
      (item) => item.display_name === displayName && item.language === language && item.icon === (draft.icon || actor.icon || ""),
    ) || room.participants[room.participants.length - 1];

  await activateRoom(room, participant, false);
}

async function saveCurrentRoomTitle() {
  if (!currentRoom || !chatRoomTitleInput) {
    return;
  }
  const nextTitle = chatRoomTitleInput.value.trim();
  if ((currentRoom.title || "").trim() === nextTitle) {
    roomTitleEditing = false;
    renderRoomHeader();
    return;
  }
  const updatedRoom = await requestJson(`/api/rooms/${roomIdToApi(currentRoom.room_id)}`, {
    method: "PATCH",
    body: JSON.stringify({
      title: nextTitle,
    }),
  });
  currentRoom = updatedRoom;
  roomTitleEditing = false;
  if (selfParticipant) {
    selfParticipant =
      updatedRoom.participants.find(
        (participant) => participant.participant_id === selfParticipant.participant_id,
      ) || selfParticipant;
  }
  if (selectedHistoryDetail?.room?.room_id === updatedRoom.room_id) {
    selectedHistoryDetail = {
      ...selectedHistoryDetail,
      room: updatedRoom,
    };
    renderHistoryDetail(selectedHistoryDetail);
  }
  mergeRoomHistorySummary({
    room_id: updatedRoom.room_id,
    room_title: updatedRoom.title || "",
    last_activity_at: updatedRoom.last_activity_at,
  });
  renderHistoryList();
  renderParticipants(updatedRoom.participants || []);
  renderRoomHeader();
}

async function ensureRoomCanBeJoined(inviteCode) {
  const previewRoom =
    roomPreviewState?.invite_code === inviteCode
      ? roomPreviewState
      : await requestJson(`/api/rooms/invites/${encodeURIComponent(inviteCode)}`);
  roomPreviewState = previewRoom;
  if ((previewRoom.participants || []).length >= roomCapacity) {
    throw new Error("This private invite is full or unavailable.");
  }
}

async function activateRoom(room, participant, createdByMe, { openChat = true } = {}) {
  const preserveReady = Boolean(
    currentRoom?.room_id === room.room_id &&
      selfParticipant?.participant_id === participant.participant_id &&
      socket?.readyState === WebSocket.OPEN &&
      roomSessionReady,
  );
  manualDisconnect = false;
  currentRoom = room;
  selfParticipant = participant;
  roomTitleEditing = false;
  roomSessionReady = preserveReady;
  endedRoomIds.delete(room.room_id);
  activeSpeaker = null;
  setSetupStatus(
    createdByMe
      ? "Private room created. Invite your partner, then open it from Lists."
      : `Joined the private room as ${participant.display_name}.`,
  );
  if (copyInviteButton) {
    copyInviteButton.disabled = false;
  }
  const url = new URL(window.location.href);
  url.searchParams.delete("room");
  if (room.invite_code) {
    url.searchParams.set("invite", room.invite_code);
  }
  window.history.replaceState({}, "", url);
  clearConversation();
  hideLiveCaption();
  if (preserveReady) {
    setMicStatus(
      mediaStream ? "micSpeakingNow" : "micReady",
      mediaStream ? { name: participant.display_name } : {},
    );
  } else {
    setMicStatus("micReconnect");
  }
  renderParticipants(room.participants);
  renderAppShareRow();
  renderInviteCard();
  renderRoomHeader();
  renderMicButtons();
  renderTextComposer();
  updateTurnGuide();
  selectedHistoryRoomId = room.room_id;
  selectedHistoryDetail = null;
  syncScreenActionButtons();
  await loadRoomHistory();
  await loadNotifications();
  if (!openChat) {
    showMyPageScreen();
    if (currentUser) {
      await openRoomHistory(room.room_id).catch(() => {});
    }
    return;
  }
  showConversationScreen();
  await loadRoomTurns(room.room_id);
  await connectRoomSocket();
}

async function loadRoomTurns(roomId) {
  const turns = await requestJson(`/api/rooms/${roomIdToApi(roomId)}/turns`);
  if (turns.length) {
    conversationEl.hidden = false;
  }
  turns.forEach((turn) => {
    if (turn.turn_type === "attachment" && turn.attachment) {
      appendAttachmentTurn({
        turnId: turn.turn_id || "",
        speakerName: turn.speaker.display_name,
        speakerParticipantId: turn.speaker.participant_id,
        speakerIcon: turn.speaker.icon || "",
        sourceLanguage: turn.source_language || turn.speaker.language || "auto",
        attachment: turn.attachment,
        createdAt: Date.parse(turn.created_at || "") || 0,
      });
      return;
    }
    const sourceLanguage = inferSourceLanguage(
      turn.source_language,
      turn.source_text,
      turn.translations || {},
    );
    appendConversationTurn({
      turnId: turn.turn_id || "",
      speakerName: turn.speaker.display_name,
      speakerParticipantId: turn.speaker.participant_id,
      speakerIcon: turn.speaker.icon || "",
      sourceLanguage,
      sourceText: turn.source_text,
      translatedText: turn.translations[counterpartLanguage(sourceLanguage)] || "",
      sourceShownAt: Date.parse(turn.created_at || "") || 0,
      translatedShownAt: Date.parse(turn.created_at || "") || 0,
    });
  });
}

async function exitCurrentRoom() {
  if (!currentRoom || !selfParticipant) {
    showMyPageScreen();
    return;
  }
  const exitedRoomId = currentRoom.room_id;
  endedRoomIds.add(exitedRoomId);
  await fetch(
    apiUrl(`/api/rooms/${encodeURIComponent(currentRoom.room_id)}/participants/${encodeURIComponent(selfParticipant.participant_id)}`),
    {
      method: "DELETE",
      credentials: "same-origin",
    },
  ).catch(() => {});
  await stopStreaming().catch(() => {});
  await disconnectRoomSocket({ intentional: true }).catch(() => {});
  currentRoom = null;
  selfParticipant = null;
  activeSpeaker = null;
  const url = new URL(window.location.href);
  url.searchParams.delete("room");
  window.history.replaceState({}, "", url);
  clearConversation();
  hideLiveCaption();
  renderParticipants([]);
  renderAppShareRow();
  renderInviteCard();
  renderRoomHeader();
  renderMicButtons();
  renderTextComposer();
  updateTurnGuide();
  selectedHistoryRoomId = exitedRoomId;
  selectedHistoryDetail = null;
  syncScreenActionButtons();
  showMyPageScreen();
  if (currentUser) {
    await loadRoomHistory();
    await loadNotifications();
    await openRoomHistory(exitedRoomId);
    return;
  }
  setSetupStatus("Exited the private room.");
}

function roomWebSocketUrl(roomId, participantId) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/rooms/${roomIdToApi(roomId)}?participant_id=${encodeURIComponent(participantId)}`;
}

async function connectRoomSocket() {
  if (!currentRoom || !selfParticipant) {
    return;
  }

  clearReconnectTimer();
  await disconnectRoomSocket({ intentional: true });
  manualDisconnect = false;
  roomSessionReady = false;
  const ws = new WebSocket(roomWebSocketUrl(currentRoom.room_id, selfParticipant.participant_id));
  const generation = (roomConnectionGeneration += 1);
  socket = ws;
  ws.binaryType = "arraybuffer";
  socketStatusEl.textContent = "Connecting room socket...";
  updateTurnGuide();

  ws.addEventListener("open", () => {
    if (socket !== ws || generation !== roomConnectionGeneration) {
      return;
    }
    reconnectAttempt = 0;
    clearHeartbeat();
    pingIntervalId = window.setInterval(() => {
      if (socket === ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "ping" }));
      }
    }, PING_INTERVAL_MS);
  });

  ws.addEventListener("message", (event) => {
    if (socket !== ws || generation !== roomConnectionGeneration) {
      return;
    }

    const data = JSON.parse(event.data);

    if (data.type === "room_ready") {
      roomSessionReady = true;
      currentRoom = {
        ...currentRoom,
        participants: data.payload.participants,
        participant_count: data.payload.participants.length,
      };
      renderParticipants(data.payload.participants);
      renderRoomHeader();
      renderMicButtons();
      renderTextComposer();
      socketStatusEl.textContent = `Connected as ${data.payload.participant.display_name}`;
      setMicStatus("micReady");
      startButton.disabled = false;
      updateTurnGuide();
      return;
    }

    if (data.type === "participant_joined") {
      if (!currentRoom) {
        return;
      }
      const nextParticipants = upsertParticipant(currentRoom.participants, data.payload.participant);
      currentRoom = {
        ...currentRoom,
        participants: nextParticipants,
        participant_count: nextParticipants.length,
      };
      renderParticipants(nextParticipants);
      renderRoomHeader();
      setSetupStatus(`${data.payload.participant.display_name} joined the room.`);
      appendSystemConversationTurn(`${data.payload.participant.display_name}님이 입장했습니다.`);
      updateTurnGuide();
      return;
    }

    if (data.type === "participant_left") {
      if (!currentRoom) {
        return;
      }
      const nextParticipants = currentRoom.participants.filter(
        (participant) => participant.participant_id !== data.payload.participant.participant_id,
      );
      currentRoom = {
        ...currentRoom,
        participants: nextParticipants,
        participant_count: nextParticipants.length,
      };
      renderParticipants(nextParticipants);
      renderRoomHeader();
      setSetupStatus(`${data.payload.participant.display_name} left the room.`);
      appendSystemConversationTurn(`${data.payload.participant.display_name}님이 퇴장했습니다.`);
      updateTurnGuide();
      return;
    }

    if (data.type === "session_started") {
      sessionStarted = true;
      setMicStatus("micLiveFor", { language: languageLabel(selfParticipant.language) });
      resetLatencyProbe({ turnActive: true });
      renderMetrics(null);
      updateTurnGuide();
      return;
    }

    if (data.type === "speaker_state") {
      activeSpeaker = {
        participantId: data.payload.speaker?.participant_id || "",
        displayName: data.payload.speaker?.display_name || "Speaker",
        active: Boolean(data.payload.active),
      };
      if (activeSpeaker.active) {
        resetLatencyProbe({ turnActive: true });
      }
      if (!activeSpeaker.active) {
        activeSpeaker = null;
      }
      renderRoomHeader();
      updateTurnGuide();
      return;
    }

    if (data.type === "partial") {
      const speakerName = data.payload.speaker?.display_name || "Speaker";
      const sourceLanguage = data.payload.language === "unknown" ? "ko" : data.payload.language;
      updateLiveCaption({
        speakerName,
        speakerParticipantId: data.payload.speaker?.participant_id || "",
        sourceLanguage,
        sourceText: data.payload.text,
        translatedText: liveTurnState?.translatedText || "",
        sourceShownAt: liveTurnState?.sourceShownAt || Date.now(),
        translatedShownAt: liveTurnState?.translatedShownAt || 0,
      });
      renderMetrics(data.payload.metrics);
      return;
    }

    if (data.type === "final") {
      lastFinalPayload = data.payload;
      renderMetrics(data.payload.metrics);
      return;
    }

    if (data.type === "translation") {
      const speakerName = data.payload.speaker?.display_name || "Speaker";
      const sourceText = data.payload.source_text || lastFinalPayload?.text || "";
      const nonverbalTurn = isNonverbalText(sourceText);
      const sourceLanguage = inferSourceLanguage(
        data.payload.source_language || lastFinalPayload?.language || "auto",
        sourceText,
        data.payload.translations || {},
      );
      const translatedText = data.payload.translations[counterpartLanguage(sourceLanguage)] || "";

      if (data.payload.is_final && sourceText && (translatedText || nonverbalTurn)) {
        noteSourceVisible();
        if (translatedText) {
          noteTranslationVisible();
        }
        appendConversationTurn({
          turnId: data.payload.turn_id || "",
          speakerName,
          speakerParticipantId: data.payload.speaker?.participant_id || "",
          speakerIcon: data.payload.speaker?.icon || "",
          sourceLanguage,
          sourceText,
          translatedText: nonverbalTurn ? "" : translatedText,
          sourceShownAt: liveTurnState?.sourceShownAt || Date.now(),
          translatedShownAt: liveTurnState?.translatedShownAt || Date.now(),
        });
        hideLiveCaption();
      } else if (sourceText) {
        updateLiveCaption({
          speakerName,
          speakerParticipantId: data.payload.speaker?.participant_id || "",
          sourceLanguage,
          sourceText,
          translatedText: nonverbalTurn ? "" : translatedText,
          sourceShownAt: liveTurnState?.sourceShownAt || Date.now(),
          translatedShownAt: liveTurnState?.translatedShownAt || Date.now(),
        });
      }

      renderMetrics(data.payload.metrics);
      if (data.payload.is_final) {
        lastFinalPayload = null;
        activeSpeaker = null;
        renderRoomHeader();
        updateTurnGuide();
      }
      return;
    }

    if (data.type === "attachment") {
      appendAttachmentTurn({
        turnId: data.payload.turn_id || "",
        speakerName: data.payload.speaker?.display_name || "Speaker",
        speakerParticipantId: data.payload.speaker?.participant_id || "",
        speakerIcon: data.payload.speaker?.icon || "",
        sourceLanguage: data.payload.source_language || data.payload.speaker?.language || "auto",
        attachment: data.payload.attachment,
        createdAt: Date.parse(data.payload.created_at || "") || Date.now(),
      });
      textStatusEl.textContent = "File sent to the room.";
      textStatusEl.hidden = false;
      return;
    }

    if (data.type === "stats") {
      renderMetrics(data.payload);
      return;
    }

    if (data.type === "error") {
      socketStatusEl.textContent = `Error: ${data.payload.message}`;
    }
  });

  ws.addEventListener("close", () => {
    if (socket !== ws || generation !== roomConnectionGeneration) {
      return;
    }
    clearHeartbeat();
    socket = null;
    roomSessionReady = false;
    activeSpeaker = null;
    sessionStarted = false;
    void releaseAudioPipeline();
    socketStatusEl.textContent = "Room socket disconnected";
    startButton.disabled = true;
    stopButton.disabled = true;
    renderTextComposer();
    setMicStatus(manualDisconnect ? "micClosed" : "micReconnect");
    renderRoomHeader();
    updateTurnGuide();

    if (!manualDisconnect && currentRoom && selfParticipant) {
      void refreshRuntimeReadiness({ silent: true });
      reconnectAttempt += 1;
      const delayMs = Math.min(1000 * 2 ** Math.min(reconnectAttempt - 1, 3), 8000);
      reconnectTimeoutId = window.setTimeout(() => {
        connectRoomSocket().catch((error) => {
          socketStatusEl.textContent = error.message;
          updateTurnGuide();
        });
      }, delayMs);
      socketStatusEl.textContent = `Room socket disconnected. Reconnecting in ${Math.round(delayMs / 1000)}s...`;
      updateTurnGuide();
    }
  });
}

async function disconnectRoomSocket({ intentional = true } = {}) {
  clearReconnectTimer();
  manualDisconnect = intentional;
  clearHeartbeat();
  if (socket) {
    socket.close();
    socket = null;
  }
  roomSessionReady = false;
  sessionStarted = false;
}

function clearHeartbeat() {
  if (pingIntervalId) {
    window.clearInterval(pingIntervalId);
    pingIntervalId = null;
  }
}

function upsertParticipant(participants, participant) {
  const next = participants.filter((item) => item.participant_id !== participant.participant_id);
  next.push(participant);
  return next;
}

function floatTo16BitPCM(float32Array) {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);
  for (let index = 0; index < float32Array.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, float32Array[index]));
    view.setInt16(index * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
  }
  return buffer;
}

async function initializeAudioPipeline() {
  const AudioContextCtor = audioContextConstructor();
  if (!AudioContextCtor) {
    throw new Error("This browser does not support realtime microphone capture.");
  }

  audioContext = new AudioContextCtor();
  if (audioContext.state === "suspended") {
    await audioContext.resume();
  }

  latestSampleRate = audioContext.sampleRate;
  sourceNode = audioContext.createMediaStreamSource(mediaStream);
  processorNode = audioContext.createScriptProcessor(2048, 1, 1);
  muteNode = audioContext.createGain();
  muteNode.gain.value = 0;

  processorNode.onaudioprocess = (event) => {
    if (!socket || socket.readyState !== WebSocket.OPEN || !sessionStarted) {
      return;
    }

    if (socket.bufferedAmount > MAX_SOCKET_BUFFERED_BYTES) {
      droppedChunkCount += 1;
      socketStatusEl.textContent = `Backpressure detected · dropped ${droppedChunkCount}`;
      return;
    }

    const inputData = event.inputBuffer.getChannelData(0);
    socket.send(floatTo16BitPCM(inputData));
  };

  sourceNode.connect(processorNode);
  processorNode.connect(muteNode);
  muteNode.connect(audioContext.destination);
}

async function startStreaming() {
  if (!socket || socket.readyState !== WebSocket.OPEN || !selfParticipant || !roomSessionReady) {
    throw new Error("Join a room first.");
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("This browser cannot access the microphone.");
  }

  startButton.disabled = true;
  stopButton.disabled = true;
  droppedChunkCount = 0;
  lastFinalPayload = null;
  setMicStatus("micRequestPermission");

  mediaStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });

  await initializeAudioPipeline();

  socket.send(
    JSON.stringify({
      type: "start",
      sample_rate: latestSampleRate,
      language: selfParticipant.language,
    }),
  );
  stopButton.disabled = false;
  setMicStatus("micSpeakingNow", { name: selfParticipant.display_name });
  renderMicButtons();
  updateTurnGuide();
}

async function stopStreaming() {
  sessionStarted = false;
  await releaseAudioPipeline();
  hideLiveCaption();
  lastFinalPayload = null;
  activeSpeaker = null;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "stop" }));
  }
  startButton.disabled = false;
  stopButton.disabled = true;
  setMicStatus("micStopped");
  renderRoomHeader();
  renderMicButtons();
  updateTurnGuide();
}

async function submitTextTurn() {
  if (!currentRoom || !selfParticipant) {
    throw new Error("Join a room first.");
  }

  const sourceText = textTurnInput.value.trim();
  if (!sourceText) {
    throw new Error(translateUi("textMessageFirst"));
  }

  textTurnSubmitting = true;
  renderTextComposer();

  try {
    await requestJson(`/api/rooms/${roomIdToApi(currentRoom.room_id)}/turns/demo`, {
      method: "POST",
      body: JSON.stringify({
        participant_id: selfParticipant.participant_id,
        language: selfParticipant.language,
        source_text: sourceText,
      }),
    });
    textTurnInput.value = "";
    textStatusEl.textContent = translateUi("textSent");
  } finally {
    textTurnSubmitting = false;
    renderTextComposer();
    if (!textTurnInput.disabled) {
      textTurnInput.focus();
    }
  }
}

async function submitAttachmentTurn(file) {
  if (!currentRoom || !selfParticipant) {
    throw new Error("Join a room first.");
  }
  if (!file) {
    throw new Error("Choose a file first.");
  }

  attachmentTurnSubmitting = true;
  renderTextComposer();

  try {
    const body = new FormData();
    body.append("participant_id", selfParticipant.participant_id);
    body.append("attachment_file", file, file.name);
    await requestJson(`/api/rooms/${roomIdToApi(currentRoom.room_id)}/turns/attachment`, {
      method: "POST",
      body,
    });
  } finally {
    attachmentTurnSubmitting = false;
    if (attachmentInput) {
      attachmentInput.value = "";
    }
    renderTextComposer();
    if (!textTurnInput.disabled) {
      textTurnInput.focus();
    }
  }
}

async function releaseAudioPipeline() {
  if (processorNode) {
    processorNode.disconnect();
    processorNode.onaudioprocess = null;
  }
  if (sourceNode) {
    sourceNode.disconnect();
  }
  if (muteNode) {
    muteNode.disconnect();
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
  }
  if (audioContext) {
    await audioContext.close();
  }

  audioContext = null;
  mediaStream = null;
  processorNode = null;
  sourceNode = null;
  muteNode = null;
  sessionStarted = false;
}

window.addEventListener("beforeunload", () => {
  if (runtimePollIntervalId) {
    window.clearInterval(runtimePollIntervalId);
    runtimePollIntervalId = null;
  }
  if (historyPollIntervalId) {
    window.clearInterval(historyPollIntervalId);
    historyPollIntervalId = null;
  }
  disconnectRoomSocket();
});
