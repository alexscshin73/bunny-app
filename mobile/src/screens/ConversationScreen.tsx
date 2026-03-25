import { useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { palette, typography } from "../theme";
import {
  ActiveSpeakerState,
  ActivityEntry,
  ConnectionState,
  ConversationTurn,
  RoomDetail,
  RoomParticipant,
} from "../types";

interface MicrophoneBridgeView {
  durationMillis: number;
  isActive: boolean;
  message: string | null;
  metering?: number;
  mode: "idle" | "preparing" | "streaming" | "recording_only" | "error";
  permissionStatus: string;
  start: () => Promise<void>;
  statusLine: string;
  stop: () => Promise<void>;
}

interface SpeechPlaybackView {
  autoplayEnabled: boolean;
  availableVoiceCounts: { ko: number; es: number };
  cycleVoice: (language: "ko" | "es") => void;
  ratePreset: "slow" | "normal" | "fast";
  selectedVoiceLabels: { ko: string; es: string };
  setAutoplayEnabled: (value: boolean) => void;
  setRatePreset: (value: "slow" | "normal" | "fast") => void;
  speakTurn: (turn: ConversationTurn) => Promise<void>;
  speakingTurnId: string | null;
  stopSpeaking: () => Promise<void>;
}

interface ConversationScreenProps {
  activeTurnParticipant: RoomParticipant;
  activeSpeakerState: ActiveSpeakerState | null;
  activityFeed: ActivityEntry[];
  backendUrl: string;
  connectionState: ConnectionState;
  errorMessage: string | null;
  isSubmitting: boolean;
  isRefreshingHistory: boolean;
  lastStats: Record<string, unknown> | null;
  liveTurns: Record<string, ConversationTurn>;
  microphone: MicrophoneBridgeView;
  isRunningDemoSequence: boolean;
  isUpdatingNotifications: boolean;
  notificationStatusText: string;
  notificationsEnabled: boolean;
  onAddDemoGuest: () => Promise<void>;
  onCycleLanguage: () => void;
  onGoHome: () => void;
  onSelectActiveTurnParticipant: (participantId: string) => void;
  onRunDemoSequence: () => Promise<void>;
  onSendDemoTurn: (participantId: string, sourceText: string) => Promise<unknown>;
  onLeaveRoom: () => void;
  onPing: () => void;
  onRefreshHistory?: () => Promise<void>;
  onSaveRoomTitle: (title: string) => Promise<unknown>;
  onToggleNotifications: () => void;
  participants: RoomParticipant[];
  room: RoomDetail;
  selfParticipant: RoomParticipant;
  speech: SpeechPlaybackView;
  turns: ConversationTurn[];
}

const DEMO_LINES: Record<RoomParticipant["language"], string[]> = {
  ko: [
    "안녕하세요, 오늘 시연을 바로 시작해볼게요.",
    "한국 팀과 멕시코 팀 일정을 함께 조율하고 싶어요.",
    "번역 자막과 음성 재생이 자연스럽게 들리는지 확인해주세요.",
  ],
  es: [
    "Hola, vamos a empezar la demo ahora mismo.",
    "Quiero coordinar el horario entre el equipo de Mexico y Corea.",
    "Por favor revisa si la traduccion y la voz suenan naturales.",
  ],
};

function stateLabel(state: ConnectionState): string {
  if (state === "connected") {
    return "Connected";
  }
  if (state === "connecting") {
    return "Connecting";
  }
  return "Disconnected";
}

function deliveryLabel(delivery: ConversationTurn["delivery"]): string {
  if (delivery === "system") {
    return "SYSTEM";
  }
  if (delivery === "demo") {
    return "DEMO";
  }
  if (delivery === "upload") {
    return "RECORDED";
  }
  return "REALTIME";
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

function formatClockTime(value?: string): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString("ko-KR", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function fallbackRoomTitle(displayName: string): string {
  const ownerName = displayName.trim() || "User";
  return `${ownerName}'s Room`;
}

export function ConversationScreen({
  activeTurnParticipant,
  activeSpeakerState,
  activityFeed,
  backendUrl,
  connectionState,
  errorMessage,
  isSubmitting,
  isRefreshingHistory,
  lastStats,
  liveTurns,
  microphone,
  isRunningDemoSequence,
  isUpdatingNotifications,
  notificationStatusText,
  notificationsEnabled,
  onAddDemoGuest,
  onCycleLanguage,
  onGoHome,
  onSelectActiveTurnParticipant,
  onRunDemoSequence,
  onSendDemoTurn,
  onLeaveRoom,
  onPing,
  onRefreshHistory,
  onSaveRoomTitle,
  onToggleNotifications,
  participants,
  room,
  selfParticipant,
  speech,
  turns,
}: ConversationScreenProps) {
  const liveTurnList = Object.values(liveTurns);
  const orderedTurns = turns.slice().reverse();
  const [selectedDemoSpeakerId, setSelectedDemoSpeakerId] = useState(activeTurnParticipant.participant_id);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [roomTitleDraft, setRoomTitleDraft] = useState(room.title?.trim() || `Room ${room.room_id}`);
  const otherParticipantSpeaking =
    activeSpeakerState?.active &&
    activeSpeakerState.speaker.participant_id !== selfParticipant.participant_id;
  const selectedDemoSpeaker =
    participants.find((participant) => participant.participant_id === selectedDemoSpeakerId) ?? activeTurnParticipant;
  const demoLines = DEMO_LINES[selectedDemoSpeaker.language];
  const demoReadiness = [
    {
      label: "Room socket",
      ready: connectionState === "connected",
      detail: stateLabel(connectionState),
    },
    {
      label: "Two speakers",
      ready: participants.length >= 2,
      detail: `${participants.length}/2 connected`,
    },
    {
      label: "History",
      ready: turns.length > 0,
      detail: `${turns.length} final turns`,
    },
    {
      label: "Voice output",
      ready: speech.availableVoiceCounts.ko + speech.availableVoiceCounts.es > 0,
      detail: `${speech.availableVoiceCounts.ko + speech.availableVoiceCounts.es} voices`,
    },
  ];
  const turnModeHeadline =
    activeSpeakerState?.active
      ? `${activeSpeakerState.speaker.display_name} is speaking now`
      : participants.length >= 2
        ? `Pass the phone to ${activeTurnParticipant.display_name}`
        : "Add a second speaker to use turn mode";
  const turnModeInstruction =
    activeSpeakerState?.active
      ? activeSpeakerState.speaker.participant_id === selfParticipant.participant_id
        ? "Your live turn is active. Finish speaking, then stop the microphone to publish the translated turn."
        : `Wait for ${activeSpeakerState.speaker.display_name} to finish before starting another microphone turn.`
      : participants.length >= 2
        ? `${activeTurnParticipant.display_name} should speak in ${activeTurnParticipant.language.toUpperCase()}, then stop recording to see the translated turn.`
        : "A second participant can be another real user or a demo guest.";
  const latestTurn = orderedTurns.find((turn) => turn.delivery !== "system") ?? null;
  const nextAction = activeSpeakerState?.active
    ? activeSpeakerState.speaker.participant_id === selfParticipant.participant_id
      ? "Finish the sentence, then stop the mic so the translated turn can land in history."
      : `Wait for ${activeSpeakerState.speaker.display_name} to finish before starting your turn.`
    : participants.length < 2
      ? "Add a second speaker or demo guest."
      : microphone.isActive
        ? "Stop recording to finalize the translated turn."
        : `Hand the phone to ${activeTurnParticipant.display_name} and start a turn.`;
  const startMicDisabled = isSubmitting || microphone.isActive || Boolean(otherParticipantSpeaking);
  const startMicLabel = otherParticipantSpeaking ? "Wait Turn" : "Start Mic";
  const roomTitle = room.title?.trim() || fallbackRoomTitle(selfParticipant.display_name);

  async function commitRoomTitle() {
    const nextTitle = roomTitleDraft.trim();
    if (nextTitle === roomTitle) {
      setIsEditingTitle(false);
      return;
    }
    await onSaveRoomTitle(nextTitle);
    setIsEditingTitle(false);
  }

  useEffect(() => {
    if (!participants.some((participant) => participant.participant_id === selectedDemoSpeakerId)) {
      setSelectedDemoSpeakerId(activeTurnParticipant.participant_id);
    }
  }, [activeTurnParticipant.participant_id, participants, selectedDemoSpeakerId]);

  useEffect(() => {
    setSelectedDemoSpeakerId(activeTurnParticipant.participant_id);
  }, [activeTurnParticipant.participant_id]);

  useEffect(() => {
    setRoomTitleDraft(roomTitle);
  }, [roomTitle]);

  return (
    <View style={styles.root}>
      <View style={styles.headerCard}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.roomLabel}>Room {room.room_id}</Text>
            <Text style={styles.roomTitle}>Realtime bilingual conversation</Text>
          </View>
          <Text style={styles.statusPill}>{stateLabel(connectionState)}</Text>
        </View>
        <View style={styles.settingsBar}>
          <View style={styles.settingsTitleGroup}>
            {isEditingTitle ? (
              <TextInput
                autoFocus
                editable={!isSubmitting}
                maxLength={80}
                onChangeText={setRoomTitleDraft}
                onSubmitEditing={() => {
                  void commitRoomTitle();
                }}
                returnKeyType="done"
                style={styles.settingsTitleInput}
                value={roomTitleDraft}
              />
            ) : (
              <Text ellipsizeMode="tail" numberOfLines={1} style={styles.settingsTitleText}>
                {roomTitle}
              </Text>
            )}
            <Pressable
              accessibilityLabel={isEditingTitle ? "Save room title" : "Edit room title"}
              onPress={() => {
                if (isEditingTitle) {
                  void commitRoomTitle();
                  return;
                }
                setRoomTitleDraft(roomTitle);
                setIsEditingTitle(true);
              }}
              style={styles.iconButton}
            >
              <Text style={styles.iconButtonText}>{isEditingTitle ? "Save" : "Edit"}</Text>
            </Pressable>
          </View>
          <View style={styles.settingsActions}>
            <Pressable accessibilityLabel="Change language" onPress={onCycleLanguage} style={styles.languageButton}>
              <Text style={styles.languageButtonText}>{selfParticipant.language.toUpperCase()}</Text>
            </Pressable>
            <Pressable
              accessibilityLabel={notificationsEnabled ? "Disable notifications" : "Enable notifications"}
              onPress={onToggleNotifications}
              style={styles.iconButton}
            >
              <Text style={styles.iconButtonText}>
                {isUpdatingNotifications ? "..." : notificationsEnabled ? "Bell" : "Mute"}
              </Text>
            </Pressable>
            <Pressable accessibilityLabel="Add participant" onPress={onAddDemoGuest} style={styles.iconButton}>
              <Text style={styles.iconButtonText}>+</Text>
            </Pressable>
            <Pressable accessibilityLabel="Home" onPress={onGoHome} style={styles.iconButton}>
              <Text style={styles.iconButtonText}>⌂</Text>
            </Pressable>
            <Pressable accessibilityLabel="Exit room" onPress={onLeaveRoom} style={styles.iconButton}>
              <Text style={styles.iconButtonText}>⇥</Text>
            </Pressable>
          </View>
        </View>
        <Text style={styles.backendText}>{backendUrl}</Text>
        <Text style={styles.notificationText}>{notificationStatusText}</Text>
        <View style={styles.participantRow}>
          {participants.map((participant) => {
            const isSelf = participant.participant_id === selfParticipant.participant_id;
            const isSpeaking =
              activeSpeakerState?.active &&
              activeSpeakerState.speaker.participant_id === participant.participant_id;
            return (
              <View
                key={participant.participant_id}
                style={[
                  styles.participantChip,
                  isSelf && styles.participantChipSelf,
                  isSpeaking && styles.participantChipSpeaking,
                ]}
              >
                <Text style={styles.participantName}>
                  {participant.display_name} {isSelf ? "You" : ""}
                </Text>
                <Text style={styles.participantLanguage}>{participant.language.toUpperCase()}</Text>
              </View>
            );
          })}
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} style={styles.scrollView}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Demo summary</Text>
          <Text style={styles.summaryHeadline}>
            Current speaker: {activeTurnParticipant.display_name} ({activeTurnParticipant.language.toUpperCase()})
          </Text>
          <Text style={styles.summaryBody}>Next action: {nextAction}</Text>
          {activeSpeakerState?.active ? (
            <View style={styles.liveSpeakerBanner}>
              <Text style={styles.liveSpeakerBannerLabel}>Live speaker</Text>
              <Text style={styles.liveSpeakerBannerTitle}>
                {activeSpeakerState.speaker.display_name} · {activeSpeakerState.language.toUpperCase()}
              </Text>
              <Text style={styles.liveSpeakerBannerBody}>
                {activeSpeakerState.speaker.participant_id === selfParticipant.participant_id
                  ? "This device is currently sending a live turn."
                  : "Listen for the translation and wait until this turn ends before starting another mic session."}
              </Text>
            </View>
          ) : null}
          {latestTurn ? (
            <View style={styles.summaryTurnCard}>
              <Text style={styles.summaryTurnLabel}>Latest translated turn</Text>
              <Text style={styles.summaryTurnSource}>{latestTurn.sourceText}</Text>
              {latestTurn.translatedText || !isNonverbalText(latestTurn.sourceText) ? (
                <Text style={styles.summaryTurnTranslation}>
                  {latestTurn.translatedText || "No translated text yet"}
                </Text>
              ) : null}
            </View>
          ) : (
            <Text style={styles.summaryBody}>
              No finalized turn yet. Use Demo lab or record a turn to populate the conversation.
            </Text>
          )}
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Single-device turn mode</Text>
          <Text style={styles.panelHint}>
            If two people are sharing one phone, pick who is speaking now before recording a turn.
          </Text>
          <View style={styles.turnModeBanner}>
            <Text style={styles.turnModeHeadline}>{turnModeHeadline}</Text>
            <Text style={styles.turnModeBody}>{turnModeInstruction}</Text>
          </View>
          <View style={styles.participantRow}>
            {participants.map((participant) => {
              const isActive = participant.participant_id === activeTurnParticipant.participant_id;
              return (
                <Pressable
                  key={`turn-${participant.participant_id}`}
                  onPress={() => onSelectActiveTurnParticipant(participant.participant_id)}
                  style={[styles.participantChip, isActive && styles.participantChipSelf]}
                >
                  <Text style={styles.participantName}>{participant.display_name}</Text>
                  <Text style={styles.participantLanguage}>{participant.language.toUpperCase()}</Text>
                </Pressable>
              );
            })}
          </View>
          <Text style={styles.demoSpeakerHint}>
            Current speaker for mic/upload: {activeTurnParticipant.display_name} (
            {activeTurnParticipant.language.toUpperCase()})
          </Text>
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Demo readiness</Text>
          <Text style={styles.panelHint}>
            This checklist makes it easy to judge whether the app is ready for a live walkthrough.
          </Text>
          <View style={styles.readinessGrid}>
            {demoReadiness.map((item) => (
              <View
                key={item.label}
                style={[styles.readinessCard, item.ready ? styles.readinessCardReady : styles.readinessCardPending]}
              >
                <Text
                  style={[
                    styles.readinessLabel,
                    item.ready ? styles.readinessLabelReady : styles.readinessLabelPending,
                  ]}
                >
                  {item.ready ? "Ready" : "Pending"} · {item.label}
                </Text>
                <Text style={styles.readinessDetail}>{item.detail}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Demo lab</Text>
          <Text style={styles.panelHint}>
            Use this panel to verify translation, history, and TTS without relying on live speech.
          </Text>
          <View style={styles.controlRow}>
            {participants.length < 2 ? (
              <Pressable disabled={isSubmitting} onPress={onAddDemoGuest} style={styles.primaryButton}>
                <Text style={styles.primaryButtonText}>
                  {isSubmitting ? "Working..." : "Add Demo Guest"}
                </Text>
              </Pressable>
            ) : null}
            <Pressable
              disabled={isSubmitting || isRunningDemoSequence}
              onPress={onRunDemoSequence}
              style={styles.secondaryButton}
            >
              <Text style={styles.secondaryButtonText}>
                {isRunningDemoSequence ? "Running Demo..." : "Run Demo Sequence"}
              </Text>
            </Pressable>
          </View>
          <Text style={styles.demoSpeakerHint}>
            One tap can now send a bilingual scripted sequence for fast demos.
          </Text>
          <View style={styles.participantRow}>
            {participants.map((participant) => {
              const isActive = participant.participant_id === selectedDemoSpeaker.participant_id;
              return (
                <Pressable
                  key={participant.participant_id}
                  onPress={() => setSelectedDemoSpeakerId(participant.participant_id)}
                  style={[styles.participantChip, isActive && styles.participantChipSelf]}
                >
                  <Text style={styles.participantName}>{participant.display_name}</Text>
                  <Text style={styles.participantLanguage}>{participant.language.toUpperCase()}</Text>
                </Pressable>
              );
            })}
          </View>
          <Text style={styles.demoSpeakerHint}>
            Selected speaker: {selectedDemoSpeaker.display_name} ({selectedDemoSpeaker.language.toUpperCase()})
          </Text>
          {demoLines.map((line) => (
            <Pressable
              key={`${selectedDemoSpeaker.language}-${line}`}
              disabled={isSubmitting || isRunningDemoSequence}
              onPress={() => onSendDemoTurn(selectedDemoSpeaker.participant_id, line)}
              style={styles.demoLineCard}
            >
              <Text style={styles.demoLineText}>{line}</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Live stage</Text>
          <Text style={styles.panelHint}>
            This view already reacts to room events and translation payloads from the backend.
          </Text>
          {liveTurnList.length === 0 ? (
            <Text style={styles.emptyText}>No live turn yet. Connect both speakers and start a session.</Text>
          ) : (
            liveTurnList.map((turn) => (
              <View key={turn.id} style={styles.liveTurnCard}>
                <Text style={styles.liveSpeaker}>{turn.speaker.display_name}</Text>
                <Text style={styles.sourceText}>{turn.sourceText}</Text>
                {turn.translatedText || !isNonverbalText(turn.sourceText) ? (
                  <Text style={styles.translationText}>{turn.translatedText || "Awaiting translation..."}</Text>
                ) : null}
              </View>
            ))
          )}
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Voice playback</Text>
          <Text style={styles.panelHint}>
            Final translations can be spoken out loud. Autoplay is intended for the other participant's turns in your language.
          </Text>
          <View style={styles.controlRow}>
            <Pressable
              onPress={() => speech.setAutoplayEnabled(!speech.autoplayEnabled)}
              style={[styles.ghostButton, speech.autoplayEnabled && styles.toggleButtonActive]}
            >
              <Text style={[styles.ghostButtonText, speech.autoplayEnabled && styles.toggleButtonTextActive]}>
                {speech.autoplayEnabled ? "Autoplay On" : "Autoplay Off"}
              </Text>
            </Pressable>
            <Pressable onPress={speech.stopSpeaking} style={styles.ghostButton}>
              <Text style={styles.ghostButtonText}>Stop Voice</Text>
            </Pressable>
          </View>
          <View style={styles.rateRow}>
            {(["slow", "normal", "fast"] as const).map((rate) => (
              <Pressable
                key={rate}
                onPress={() => speech.setRatePreset(rate)}
                style={[styles.rateChip, speech.ratePreset === rate && styles.rateChipActive]}
              >
                <Text style={[styles.rateChipText, speech.ratePreset === rate && styles.rateChipTextActive]}>
                  {rate.toUpperCase()}
                </Text>
              </Pressable>
            ))}
          </View>
          <View style={styles.voiceCard}>
            <Text style={styles.voiceTitle}>Korean voice</Text>
            <Text style={styles.voiceLabel}>{speech.selectedVoiceLabels.ko}</Text>
            <Text style={styles.voiceMeta}>{speech.availableVoiceCounts.ko} voices available</Text>
            <Pressable onPress={() => speech.cycleVoice("ko")} style={styles.inlineAction}>
              <Text style={styles.inlineActionText}>Switch Korean Voice</Text>
            </Pressable>
          </View>
          <View style={styles.voiceCard}>
            <Text style={styles.voiceTitle}>Spanish voice</Text>
            <Text style={styles.voiceLabel}>{speech.selectedVoiceLabels.es}</Text>
            <Text style={styles.voiceMeta}>{speech.availableVoiceCounts.es} voices available</Text>
            <Pressable onPress={() => speech.cycleVoice("es")} style={styles.inlineAction}>
              <Text style={styles.inlineActionText}>Switch Spanish Voice</Text>
            </Pressable>
          </View>
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Conversation history</Text>
          <View style={styles.controlRow}>
            <Pressable
              disabled={!onRefreshHistory || isRefreshingHistory}
              onPress={onRefreshHistory}
              style={styles.ghostButton}
            >
              <Text style={styles.ghostButtonText}>
                {isRefreshingHistory ? "Refreshing..." : "Refresh History"}
              </Text>
            </Pressable>
          </View>
          {turns.length === 0 ? (
            <Text style={styles.emptyText}>Finalized turns will land here once translation events are emitted.</Text>
          ) : (
            orderedTurns.map((turn, index) => (
              turn.delivery === "system" ? (
                <View key={turn.id} style={styles.systemHistoryCard}>
                  <View style={styles.systemHistoryHeader}>
                    <Text style={styles.systemHistorySpeaker}>알림</Text>
                    <Text style={styles.systemHistoryMeta}>{formatClockTime(turn.createdAt)}</Text>
                  </View>
                  <Text style={styles.systemTurnText}>{turn.sourceText}</Text>
                </View>
              ) : (
                <View key={turn.id} style={styles.historyCard}>
                  <View style={styles.historyHeader}>
                    <View>
                      <Text style={styles.historySpeaker}>{turn.speaker.display_name}</Text>
                      <Text style={styles.historyMeta}>
                        {turn.sourceLanguage.toUpperCase()} speaker
                      </Text>
                    </View>
                    <View style={[styles.deliveryBadge, index === 0 && styles.deliveryBadgeLatest]}>
                      <Text style={[styles.deliveryBadgeText, index === 0 && styles.deliveryBadgeTextLatest]}>
                        {index === 0 ? "LATEST · " : ""}
                        {deliveryLabel(turn.delivery)}
                      </Text>
                    </View>
                  </View>
                  <View style={styles.historyBlock}>
                    <Text style={styles.historyBlockLabel}>Original</Text>
                    <Text style={styles.sourceText}>{turn.sourceText}</Text>
                  </View>
                  <View style={[styles.historyBlock, styles.historyBlockTranslated]}>
                    <Text style={styles.historyBlockLabel}>Translated</Text>
                    {turn.translatedText || !isNonverbalText(turn.sourceText) ? (
                      <Text style={styles.translationText}>{turn.translatedText || "No translated text yet"}</Text>
                    ) : null}
                  </View>
                  <View style={styles.historyActionRow}>
                    <Pressable onPress={() => speech.speakTurn(turn)} style={styles.inlineAction}>
                      <Text style={styles.inlineActionText}>
                        {speech.speakingTurnId === turn.id ? "Speaking..." : "Play Voice"}
                      </Text>
                    </Pressable>
                  </View>
                </View>
              )
              ))
          )}
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Microphone bridge</Text>
          <Text style={styles.panelHint}>
            Web builds now stream realtime PCM chunks into the room socket. On iOS and Android in Expo managed runtime, the official recorder gives permission, metering, and local capture, but not raw mic PCM callbacks yet.
          </Text>
          <View style={styles.turnModeBannerSoft}>
            <Text style={styles.turnModeHeadlineSoft}>
              Recording for {activeTurnParticipant.display_name} ({activeTurnParticipant.language.toUpperCase()})
            </Text>
            <Text style={styles.turnModeBodySoft}>
              In single-device mode, the next recorded upload will be saved as this speaker's turn.
            </Text>
          </View>
          <View style={styles.statsCard}>
            <Text style={styles.statsText}>state: {microphone.statusLine}</Text>
            <Text style={styles.statsText}>permission: {microphone.permissionStatus}</Text>
            <Text style={styles.statsText}>duration_ms: {Math.round(microphone.durationMillis)}</Text>
            <Text style={styles.statsText}>
              metering: {microphone.metering == null ? "n/a" : microphone.metering.toFixed(1)}
            </Text>
          </View>
          <View style={styles.controlRow}>
            <Pressable
              disabled={startMicDisabled}
              onPress={microphone.start}
              style={[styles.primaryButton, startMicDisabled && styles.buttonDisabled]}
            >
              <Text style={styles.primaryButtonText}>{startMicLabel}</Text>
            </Pressable>
            <Pressable disabled={!microphone.isActive} onPress={microphone.stop} style={styles.secondaryButton}>
              <Text style={styles.secondaryButtonText}>Stop Mic</Text>
            </Pressable>
          </View>
          {otherParticipantSpeaking ? (
            <Text style={styles.infoText}>
              {activeSpeakerState?.speaker.display_name} is already speaking, so microphone start is paused until that
              live turn ends.
            </Text>
          ) : null}
          <View style={styles.controlRow}>
            <Pressable onPress={onPing} style={styles.ghostButton}>
              <Text style={styles.ghostButtonText}>Ping Stats</Text>
            </Pressable>
          </View>
          {microphone.message ? <Text style={styles.infoText}>{microphone.message}</Text> : null}
          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
          {lastStats ? (
            <View style={styles.statsCard}>
              {Object.entries(lastStats).map(([key, value]) => (
                <Text key={key} style={styles.statsText}>
                  {key}: {String(value)}
                </Text>
              ))}
            </View>
          ) : null}
        </View>

        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Room activity</Text>
          {activityFeed.length === 0 ? (
            <Text style={styles.emptyText}>Connection and presence events will appear here.</Text>
          ) : (
            activityFeed.map((entry) => (
              <Text key={entry.id} style={styles.activityText}>
                {entry.message}
              </Text>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: palette.canvas,
  },
  headerCard: {
    backgroundColor: palette.panel,
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
    gap: 12,
    paddingHorizontal: 20,
    paddingBottom: 18,
    paddingTop: 18,
  },
  headerTop: {
    alignItems: "flex-start",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  settingsBar: {
    alignItems: "center",
    flexDirection: "row",
    gap: 8,
  },
  settingsTitleGroup: {
    alignItems: "center",
    flex: 1,
    flexDirection: "row",
    gap: 2,
    minWidth: 0,
    paddingHorizontal: 0,
    paddingVertical: 0,
  },
  settingsTitleText: {
    color: "#778899",
    flex: 1,
    fontFamily: typography.display,
    fontSize: 20,
    minWidth: 0,
  },
  settingsTitleInput: {
    backgroundColor: "transparent",
    color: "#778899",
    flex: 1,
    fontFamily: typography.display,
    fontSize: 20,
    minWidth: 0,
    paddingHorizontal: 10,
    paddingVertical: 0,
  },
  settingsActions: {
    alignItems: "center",
    flexDirection: "row",
    flexShrink: 0,
    gap: 6,
  },
  languageButton: {
    alignItems: "center",
    backgroundColor: "#fbf4e8",
    borderColor: palette.line,
    borderRadius: 18,
    borderWidth: 1,
    height: 36,
    justifyContent: "center",
    minWidth: 54,
    paddingHorizontal: 10,
  },
  languageButtonText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 13,
  },
  iconButton: {
    alignItems: "center",
    backgroundColor: "#fbf4e8",
    borderColor: palette.line,
    borderRadius: 18,
    borderWidth: 1,
    height: 36,
    justifyContent: "center",
    minWidth: 36,
    paddingHorizontal: 10,
  },
  iconButtonText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 13,
    lineHeight: 16,
    textAlign: "center",
  },
  roomLabel: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 13,
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  roomTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 28,
    lineHeight: 34,
    marginTop: 4,
  },
  statusPill: {
    backgroundColor: palette.panelAlt,
    borderRadius: 999,
    color: palette.success,
    fontFamily: typography.body,
    overflow: "hidden",
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  backendText: {
    color: palette.inkSoft,
    fontFamily: typography.mono,
    fontSize: 12,
  },
  notificationText: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 12,
    lineHeight: 18,
  },
  participantRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  participantChip: {
    backgroundColor: "#fbf4e8",
    borderColor: palette.line,
    borderRadius: 18,
    borderWidth: 1,
    minWidth: 120,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  participantChipSelf: {
    backgroundColor: "#f5d8c7",
  },
  participantChipSpeaking: {
    borderColor: palette.accentDeep,
    borderWidth: 2,
  },
  participantName: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 15,
  },
  participantLanguage: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 1,
    marginTop: 3,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    gap: 16,
    padding: 18,
    paddingBottom: 32,
  },
  summaryCard: {
    backgroundColor: "#f0e1cc",
    borderColor: palette.line,
    borderRadius: 24,
    borderWidth: 1,
    gap: 10,
    padding: 18,
  },
  summaryLabel: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  summaryHeadline: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 26,
    lineHeight: 32,
  },
  summaryBody: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
  summaryTurnCard: {
    backgroundColor: "#fff9ef",
    borderRadius: 18,
    gap: 6,
    padding: 14,
  },
  liveSpeakerBanner: {
    backgroundColor: "#fff3d8",
    borderColor: "#e0af4b",
    borderRadius: 18,
    borderWidth: 1,
    gap: 6,
    padding: 14,
  },
  liveSpeakerBannerLabel: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  liveSpeakerBannerTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 22,
    lineHeight: 28,
  },
  liveSpeakerBannerBody: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
  summaryTurnLabel: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  summaryTurnSource: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 23,
  },
  summaryTurnTranslation: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
  },
  panel: {
    backgroundColor: palette.panel,
    borderColor: palette.line,
    borderRadius: 24,
    borderWidth: 1,
    gap: 10,
    padding: 18,
  },
  panelTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 24,
  },
  panelHint: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
  turnModeBanner: {
    backgroundColor: "#f5d8c7",
    borderRadius: 18,
    gap: 6,
    padding: 14,
  },
  turnModeHeadline: {
    color: palette.accentDeep,
    fontFamily: typography.display,
    fontSize: 22,
  },
  turnModeBody: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
  turnModeBannerSoft: {
    backgroundColor: "#f8f2e8",
    borderRadius: 18,
    gap: 6,
    padding: 14,
  },
  turnModeHeadlineSoft: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 20,
  },
  turnModeBodySoft: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
  readinessGrid: {
    gap: 10,
  },
  readinessCard: {
    borderRadius: 18,
    borderWidth: 1,
    gap: 4,
    padding: 14,
  },
  readinessCardReady: {
    backgroundColor: "#eef7f2",
    borderColor: "#b7d9c5",
  },
  readinessCardPending: {
    backgroundColor: "#fff5ec",
    borderColor: "#efc2ab",
  },
  readinessLabel: {
    fontFamily: typography.display,
    fontSize: 18,
  },
  readinessLabelReady: {
    color: palette.success,
  },
  readinessLabelPending: {
    color: palette.accentDeep,
  },
  readinessDetail: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
  },
  demoSpeakerHint: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 13,
  },
  demoLineCard: {
    backgroundColor: "#f8f2e8",
    borderColor: palette.line,
    borderRadius: 18,
    borderWidth: 1,
    padding: 14,
  },
  demoLineText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
  },
  emptyText: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
  },
  liveTurnCard: {
    backgroundColor: palette.panelAlt,
    borderRadius: 18,
    gap: 8,
    padding: 14,
  },
  liveSpeaker: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 13,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  historyCard: {
    borderColor: palette.line,
    borderRadius: 18,
    borderWidth: 1,
    gap: 10,
    padding: 14,
  },
  systemHistoryCard: {
    borderColor: "rgba(119, 136, 153, 0.22)",
    borderRadius: 18,
    borderWidth: 1,
    gap: 10,
    padding: 14,
    backgroundColor: "rgba(119, 136, 153, 0.08)",
  },
  systemHistoryHeader: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  systemHistorySpeaker: {
    color: "#778899",
    fontFamily: typography.body,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  systemHistoryMeta: {
    color: "#778899",
    fontFamily: typography.body,
    fontSize: 12,
  },
  systemTurnText: {
    color: "#778899",
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 22,
  },
  historyHeader: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  historyActionRow: {
    flexDirection: "row",
    justifyContent: "flex-end",
    marginTop: 6,
  },
  historySpeaker: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 22,
  },
  historyMeta: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 13,
  },
  deliveryBadge: {
    backgroundColor: "#f7efe3",
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  deliveryBadgeLatest: {
    backgroundColor: "#f5d8c7",
  },
  deliveryBadgeText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 0.5,
  },
  deliveryBadgeTextLatest: {
    color: palette.accentDeep,
  },
  historyBlock: {
    backgroundColor: "#fcf7ef",
    borderRadius: 16,
    gap: 6,
    padding: 12,
  },
  historyBlockTranslated: {
    backgroundColor: "#f8efe4",
  },
  historyBlockLabel: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  inlineAction: {
    backgroundColor: "#f7efe3",
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  inlineActionText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 13,
  },
  sourceText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 17,
    lineHeight: 24,
  },
  translationText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 23,
  },
  controlRow: {
    flexDirection: "row",
    gap: 10,
  },
  primaryButton: {
    backgroundColor: palette.accent,
    borderRadius: 18,
    flex: 1,
    paddingVertical: 14,
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  primaryButtonText: {
    color: "#fffaf2",
    fontFamily: typography.body,
    fontSize: 16,
    textAlign: "center",
  },
  secondaryButton: {
    borderColor: palette.accent,
    borderRadius: 18,
    borderWidth: 1,
    flex: 1,
    paddingVertical: 14,
  },
  secondaryButtonText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 16,
    textAlign: "center",
  },
  ghostButton: {
    backgroundColor: "#f7efe3",
    borderRadius: 18,
    flex: 1,
    paddingVertical: 14,
  },
  rateRow: {
    flexDirection: "row",
    gap: 10,
  },
  rateChip: {
    backgroundColor: "#f7efe3",
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  rateChipActive: {
    backgroundColor: palette.accent,
  },
  rateChipText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 13,
  },
  rateChipTextActive: {
    color: "#fffaf2",
  },
  voiceCard: {
    backgroundColor: "#f8f2e8",
    borderRadius: 18,
    gap: 6,
    padding: 14,
  },
  voiceTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 20,
  },
  voiceLabel: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 15,
  },
  voiceMeta: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 13,
  },
  toggleButtonActive: {
    backgroundColor: palette.accent,
  },
  ghostButtonText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 15,
    textAlign: "center",
  },
  toggleButtonTextActive: {
    color: "#fffaf2",
  },
  errorText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 14,
  },
  infoText: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
  },
  statsCard: {
    backgroundColor: "#f8f2e8",
    borderRadius: 18,
    gap: 4,
    padding: 12,
  },
  statsText: {
    color: palette.inkSoft,
    fontFamily: typography.mono,
    fontSize: 12,
  },
  activityText: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
  },
});
