import { StatusBar } from "expo-status-bar";
import { useEffect, useRef, useState } from "react";
import { SafeAreaView, StyleSheet } from "react-native";

import { ConversationScreen } from "./src/screens/ConversationScreen";
import { useDeviceNotifications } from "./src/hooks/useDeviceNotifications";
import { useMicrophoneBridge } from "./src/hooks/useMicrophoneBridge";
import { JoinScreen } from "./src/screens/JoinScreen";
import { useRoomSession } from "./src/hooks/useRoomSession";
import { useSpeechPlayback } from "./src/hooks/useSpeechPlayback";
import { BACKEND_PRESETS } from "./src/config";
import { SupportedLanguage } from "./src/types";
import { palette } from "./src/theme";

export default function App() {
  const session = useRoomSession();
  const microphone = useMicrophoneBridge({
    canStream: session.connectionState === "connected" && !!session.selfParticipant,
    language: session.activeTurnParticipant?.language ?? session.selfParticipant?.language ?? "ko",
    onNativeRecordingReady: session.uploadNativeRecording,
    onSendAudioChunk: session.sendAudioChunk,
    onStartSession: session.startSession,
    onStopSession: session.stopSession,
  });
  const speech = useSpeechPlayback({
    latestTurn: session.latestDeliveredTurn,
    selfLanguage: session.selfParticipant?.language ?? null,
  });
  const notifications = useDeviceNotifications();
  const [displayName, setDisplayName] = useState("Minji");
  const [language, setLanguage] = useState<SupportedLanguage>("ko");
  const [inviteCode, setInviteCode] = useState("");
  const lastNotifiedTurnIdRef = useRef<string | null>(null);
  const lastNotifiedActivityIdRef = useRef<string | null>(null);

  useEffect(() => {
    const latestTurn = session.latestDeliveredTurn;
    const selfParticipantId = session.selfParticipant?.participant_id ?? null;
    if (
      !latestTurn ||
      latestTurn.delivery === "system" ||
      latestTurn.id === lastNotifiedTurnIdRef.current ||
      latestTurn.speaker.participant_id === selfParticipantId
    ) {
      return;
    }

    lastNotifiedTurnIdRef.current = latestTurn.id;
    const roomTitle = session.room?.title?.trim() || "conversation";
    const preview = latestTurn.sourceText.trim();
    const body = preview
      ? `${latestTurn.speaker.display_name}: ${preview.slice(0, 80)}`
      : `${latestTurn.speaker.display_name} sent a new message.`;
    void notifications.notifyConversationUpdate({
      title: `New message in ${roomTitle}`,
      body,
      data: session.room?.room_id ? { roomId: session.room.room_id } : undefined,
    });
  }, [
    notifications,
    session.latestDeliveredTurn,
    session.room?.room_id,
    session.room?.title,
    session.selfParticipant?.participant_id,
  ]);

  useEffect(() => {
    const latestActivity = session.activityFeed[0];
    if (!latestActivity || latestActivity.id === lastNotifiedActivityIdRef.current) {
      return;
    }
    lastNotifiedActivityIdRef.current = latestActivity.id;

    if (!latestActivity.message.endsWith(" joined the room.")) {
      return;
    }

    const joinedName = latestActivity.message.replace(/ joined the room\.$/, "");
    if (joinedName === session.selfParticipant?.display_name) {
      return;
    }

    const roomTitle = session.room?.title?.trim() || "conversation";
    void notifications.notifyConversationUpdate({
      title: `Someone joined ${roomTitle}`,
      body: `${joinedName} joined the room.`,
      data: session.room?.room_id ? { roomId: session.room.room_id } : undefined,
    });
  }, [notifications, session.activityFeed, session.room?.room_id, session.room?.title, session.selfParticipant?.display_name]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      {session.room && session.selfParticipant ? (
        <ConversationScreen
          activeTurnParticipant={session.activeTurnParticipant ?? session.selfParticipant}
          activeSpeakerState={session.activeSpeakerState}
          activityFeed={session.activityFeed}
          backendUrl={session.backendUrl}
          connectionState={session.connectionState}
          errorMessage={session.errorMessage}
          isSubmitting={session.isSubmitting}
          isRefreshingHistory={session.isRefreshingHistory}
          isRunningDemoSequence={session.isRunningDemoSequence}
          lastStats={session.lastStats}
          liveTurns={session.liveTurns}
          microphone={microphone}
          onAddDemoGuest={session.addDemoGuest}
          onCycleLanguage={session.cycleSelfLanguage}
          onGoHome={session.goHome}
          onLeaveRoom={session.leaveRoom}
          onPing={session.ping}
          onRefreshHistory={session.refreshRoomHistory}
          onSaveRoomTitle={session.saveRoomTitle}
          onSelectActiveTurnParticipant={session.setActiveTurnParticipant}
          onToggleNotifications={() =>
            notifications.setNotificationsEnabled(!notifications.notificationsEnabled)
          }
          onRunDemoSequence={session.runDemoSequence}
          onSendDemoTurn={session.sendDemoTurn}
          notificationStatusText={notifications.notificationStatusText}
          notificationsEnabled={notifications.notificationsEnabled}
          isUpdatingNotifications={notifications.isUpdatingNotifications}
          participants={session.room.participants}
          room={session.room}
          selfParticipant={session.selfParticipant}
          speech={speech}
          turns={session.turns}
        />
      ) : (
        <JoinScreen
          backendHealth={session.backendHealth}
          backendHealthError={session.backendHealthError}
          backendUrl={session.backendUrl}
          backendPresets={BACKEND_PRESETS}
          displayName={displayName}
          errorMessage={session.errorMessage}
          isCheckingBackendHealth={session.isCheckingBackendHealth}
          isSubmitting={session.isSubmitting}
          language={language}
          notificationStatusText={notifications.notificationStatusText}
          notificationsEnabled={notifications.notificationsEnabled}
          isUpdatingNotifications={notifications.isUpdatingNotifications}
          onBackendUrlChange={session.setBackendUrl}
          onCreateRoom={() => session.createRoom({ displayName, language })}
          onDisplayNameChange={setDisplayName}
          onJoinRoom={() => session.joinRoom({ displayName, language, inviteCode })}
          onLanguageChange={setLanguage}
          onNotificationsEnabledChange={notifications.setNotificationsEnabled}
          onRefreshBackendHealth={session.refreshBackendHealth}
          onInviteCodeChange={setInviteCode}
          platformStatusText={notifications.platformStatusText}
          inviteCode={inviteCode}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: palette.canvas,
  },
});
