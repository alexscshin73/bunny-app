import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { BackendPreset, SUPPORTED_LANGUAGES } from "../config";
import { palette, typography } from "../theme";
import { BackendHealth, SupportedLanguage } from "../types";

interface JoinScreenProps {
  backendHealth: BackendHealth | null;
  backendHealthError: string | null;
  backendUrl: string;
  backendPresets: BackendPreset[];
  displayName: string;
  errorMessage: string | null;
  isCheckingBackendHealth: boolean;
  isUpdatingNotifications: boolean;
  isSubmitting: boolean;
  language: SupportedLanguage;
  onBackendUrlChange: (value: string) => void;
  onCreateRoom: () => void;
  onDisplayNameChange: (value: string) => void;
  onInviteCodeChange: (value: string) => void;
  onJoinRoom: () => void;
  onLanguageChange: (value: SupportedLanguage) => void;
  onNotificationsEnabledChange: (value: boolean) => void;
  onRefreshBackendHealth: () => void;
  notificationStatusText: string;
  notificationsEnabled: boolean;
  platformStatusText: string;
  inviteCode: string;
}

export function JoinScreen({
  backendHealth,
  backendHealthError,
  backendUrl,
  backendPresets,
  displayName,
  errorMessage,
  isCheckingBackendHealth,
  isUpdatingNotifications,
  isSubmitting,
  language,
  onBackendUrlChange,
  onCreateRoom,
  onDisplayNameChange,
  onInviteCodeChange,
  onJoinRoom,
  onLanguageChange,
  onNotificationsEnabledChange,
  onRefreshBackendHealth,
  notificationStatusText,
  notificationsEnabled,
  platformStatusText,
  inviteCode,
}: JoinScreenProps) {
  const backendReady = backendHealth?.status === "ok";
  const submitDisabled = isSubmitting || isCheckingBackendHealth || !backendReady;
  const submitHint = isCheckingBackendHealth
    ? "Checking backend health before room actions."
    : backendReady
      ? null
      : backendHealthError
        ? "Room actions are disabled until the backend health check succeeds."
        : "Set a reachable backend URL to enable room actions.";

  return (
    <View style={styles.root}>
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>Bunny App</Text>
        <Text style={styles.title}>Korean and Mexican users, one live conversation room.</Text>
        <Text style={styles.subtitle}>
          Invite-based room entry, realtime events, native recorded-turn upload, and on-device
          alerts are now aligned with the current backend.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Session Setup</Text>

        <Text style={styles.label}>Backend URL</Text>
        <TextInput
          autoCapitalize="none"
          autoCorrect={false}
          onChangeText={onBackendUrlChange}
          placeholder="http://127.0.0.1:8000"
          placeholderTextColor={palette.inkSoft}
          style={styles.input}
          value={backendUrl}
        />
        <View style={styles.backendPresetRow}>
          {backendPresets.map((preset) => {
            const isActive = preset.url === backendUrl;
            return (
              <Pressable
                key={`${preset.label}-${preset.url}`}
                onPress={() => onBackendUrlChange(preset.url)}
                style={[styles.backendPresetChip, isActive && styles.backendPresetChipActive]}
              >
                <Text
                  style={[styles.backendPresetText, isActive && styles.backendPresetTextActive]}
                >
                  {preset.label}
                </Text>
              </Pressable>
            );
          })}
        </View>
        <View style={styles.backendStatusRow}>
          <Text style={styles.backendHint}>Saved on this device and reused on the next app launch.</Text>
          <Pressable onPress={onRefreshBackendHealth} style={styles.backendRefreshButton}>
            <Text style={styles.backendRefreshText}>
              {isCheckingBackendHealth ? "Checking..." : "Refresh"}
            </Text>
          </Pressable>
        </View>
        {backendHealth ? (
          <View style={styles.healthCard}>
            <Text style={styles.healthTitle}>Backend Connected</Text>
            <Text style={styles.healthBody}>
              Store: {backendHealth.room_store.backend} / max {backendHealth.room_store.max_participants}
            </Text>
            <Text style={styles.healthBody}>
              ASR: {backendHealth.asr.engine} ({backendHealth.asr.ready ? "ready" : "not ready"})
            </Text>
            <Text style={styles.healthBody}>
              Translation: {backendHealth.translation.engine} (
              {backendHealth.translation.ready ? "ready" : "not ready"})
            </Text>
            <Text style={styles.healthBody}>
              Targets: {backendHealth.translation.targets.join(", ")}
            </Text>
            <Text style={styles.healthBody}>
              TTL: {backendHealth.room_store.ttl_minutes} min / cleanup every{" "}
              {backendHealth.room_store.cleanup_interval_seconds}s
            </Text>
          </View>
        ) : backendHealthError ? (
          <View style={styles.healthCardWarning}>
            <Text style={styles.healthTitleWarning}>Backend Unreachable</Text>
            <Text style={styles.healthBodyWarning}>{backendHealthError}</Text>
          </View>
        ) : null}

        <Text style={styles.label}>Display Name</Text>
        <TextInput
          autoCapitalize="words"
          onChangeText={onDisplayNameChange}
          placeholder="Minji"
          placeholderTextColor={palette.inkSoft}
          style={styles.input}
          value={displayName}
        />

        <Text style={styles.label}>Your Language</Text>
        <View style={styles.languageRow}>
          {SUPPORTED_LANGUAGES.map((option) => {
            const isActive = option.code === language;
            return (
              <Pressable
                key={option.code}
                onPress={() => onLanguageChange(option.code)}
                style={[styles.languageChip, isActive && styles.languageChipActive]}
              >
                <Text style={[styles.languageText, isActive && styles.languageTextActive]}>
                  {option.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        <Text style={styles.label}>Notifications</Text>
        <View style={styles.languageRow}>
          {[
            { label: "Yes", value: true },
            { label: "No", value: false },
          ].map((option) => {
            const isActive = option.value === notificationsEnabled;
            return (
              <Pressable
                key={option.label}
                disabled={isUpdatingNotifications}
                onPress={() => onNotificationsEnabledChange(option.value)}
                style={[styles.languageChip, isActive && styles.languageChipActive]}
              >
                <Text style={[styles.languageText, isActive && styles.languageTextActive]}>
                  {isUpdatingNotifications && isActive ? "Saving..." : option.label}
                </Text>
              </Pressable>
            );
          })}
        </View>
        <Text style={styles.submitHint}>{notificationStatusText}</Text>

        <Text style={styles.label}>Invite Code</Text>
        <TextInput
          autoCapitalize="none"
          autoCorrect={false}
          onChangeText={onInviteCodeChange}
          placeholder="private invite code"
          placeholderTextColor={palette.inkSoft}
          style={styles.input}
          value={inviteCode}
        />

        {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
        {submitHint ? <Text style={styles.submitHint}>{submitHint}</Text> : null}

        <View style={styles.actionRow}>
          <Pressable
            disabled={submitDisabled}
            onPress={onCreateRoom}
            style={[styles.primaryButton, submitDisabled && styles.buttonDisabled]}
          >
            <Text style={styles.primaryButtonText}>
              {isSubmitting ? "Working..." : isCheckingBackendHealth ? "Checking..." : "Create Room"}
            </Text>
          </Pressable>

          <Pressable
            disabled={submitDisabled}
            onPress={onJoinRoom}
            style={[styles.secondaryButton, submitDisabled && styles.secondaryButtonDisabled]}
          >
            <Text style={[styles.secondaryButtonText, submitDisabled && styles.secondaryButtonTextDisabled]}>
              {isCheckingBackendHealth ? "Checking..." : "Join by Invite"}
            </Text>
          </Pressable>
        </View>
      </View>

      <View style={styles.noteCard}>
        <Text style={styles.noteTitle}>Mobile notes</Text>
        <Text style={styles.noteBody}>
          This build now follows the same invite-based join flow as the web app. Creating brand-new
          rooms still depends on the signed-in account flow that exists on the web backend today.
        </Text>
        <Text style={styles.noteBody}>{platformStatusText}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    paddingHorizontal: 20,
    paddingVertical: 24,
    backgroundColor: palette.canvas,
    justifyContent: "space-between",
  },
  hero: {
    gap: 12,
    paddingTop: 18,
  },
  eyebrow: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 14,
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  title: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 38,
    lineHeight: 44,
  },
  subtitle: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 24,
  },
  card: {
    backgroundColor: palette.panel,
    borderColor: palette.line,
    borderRadius: 28,
    borderWidth: 1,
    elevation: 3,
    gap: 10,
    padding: 20,
    shadowColor: palette.shadow,
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 1,
    shadowRadius: 24,
  },
  sectionTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 26,
    marginBottom: 4,
  },
  label: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 13,
    letterSpacing: 1,
    marginTop: 6,
    textTransform: "uppercase",
  },
  input: {
    backgroundColor: "#fffdf8",
    borderColor: palette.line,
    borderRadius: 16,
    borderWidth: 1,
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 16,
    paddingHorizontal: 14,
    paddingVertical: 14,
  },
  backendPresetRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 4,
  },
  backendPresetChip: {
    backgroundColor: palette.panelAlt,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  backendPresetChipActive: {
    backgroundColor: palette.accentDeep,
  },
  backendPresetText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 13,
  },
  backendPresetTextActive: {
    color: "#fffaf2",
  },
  backendHint: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 12,
    lineHeight: 18,
    marginTop: 2,
  },
  backendStatusRow: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 2,
  },
  backendRefreshButton: {
    borderColor: palette.line,
    borderRadius: 999,
    borderWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  backendRefreshText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 13,
  },
  healthCard: {
    backgroundColor: "#eef7f2",
    borderColor: "#b7d9c5",
    borderRadius: 18,
    borderWidth: 1,
    gap: 4,
    marginTop: 8,
    padding: 14,
  },
  healthCardWarning: {
    backgroundColor: "#fff2eb",
    borderColor: "#efc2ab",
    borderRadius: 18,
    borderWidth: 1,
    gap: 4,
    marginTop: 8,
    padding: 14,
  },
  healthTitle: {
    color: palette.success,
    fontFamily: typography.display,
    fontSize: 18,
  },
  healthTitleWarning: {
    color: palette.accentDeep,
    fontFamily: typography.display,
    fontSize: 18,
  },
  healthBody: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
  },
  healthBodyWarning: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
  },
  languageRow: {
    flexDirection: "row",
    gap: 10,
  },
  languageChip: {
    backgroundColor: palette.panelAlt,
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  languageChipActive: {
    backgroundColor: palette.accent,
  },
  languageText: {
    color: palette.ink,
    fontFamily: typography.body,
    fontSize: 15,
  },
  languageTextActive: {
    color: "#fffaf2",
  },
  errorText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 14,
    marginTop: 4,
  },
  submitHint: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 13,
    lineHeight: 19,
    marginTop: 2,
  },
  actionRow: {
    flexDirection: "row",
    gap: 12,
    marginTop: 10,
  },
  primaryButton: {
    backgroundColor: palette.accent,
    borderRadius: 18,
    flex: 1,
    paddingVertical: 15,
  },
  buttonDisabled: {
    backgroundColor: "#d7b59f",
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
    paddingVertical: 15,
  },
  secondaryButtonDisabled: {
    borderColor: palette.line,
  },
  secondaryButtonText: {
    color: palette.accentDeep,
    fontFamily: typography.body,
    fontSize: 16,
    textAlign: "center",
  },
  secondaryButtonTextDisabled: {
    color: palette.inkSoft,
  },
  noteCard: {
    backgroundColor: "#ead8bf",
    borderRadius: 24,
    gap: 8,
    padding: 18,
  },
  noteTitle: {
    color: palette.ink,
    fontFamily: typography.display,
    fontSize: 22,
  },
  noteBody: {
    color: palette.inkSoft,
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
  },
});
