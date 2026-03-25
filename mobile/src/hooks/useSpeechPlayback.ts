import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Speech from "expo-speech";
import { useEffectEvent } from "react";
import { useEffect, useRef, useState } from "react";

import { ConversationTurn, SupportedLanguage } from "../types";

type SpeechRatePreset = "slow" | "normal" | "fast";
type SelectedVoiceIds = Record<SupportedLanguage, string | null>;

interface UseSpeechPlaybackOptions {
  latestTurn: ConversationTurn | null;
  selfLanguage: SupportedLanguage | null;
}

const SPEECH_PREFERENCES_KEY = "bunny_app:speech_preferences";

function isVoiceForLanguage(voice: Speech.Voice, language: SupportedLanguage): boolean {
  return voice.language.toLowerCase().startsWith(language);
}

function speechLanguage(language: SupportedLanguage): string {
  if (language === "ko") {
    return "ko-KR";
  }
  return "es-MX";
}

function speechRateValue(ratePreset: SpeechRatePreset): number {
  if (ratePreset === "slow") {
    return 0.82;
  }
  if (ratePreset === "fast") {
    return 1.05;
  }
  return 0.95;
}

function chooseInitialVoice(
  voices: Speech.Voice[],
  language: SupportedLanguage
): Speech.Voice | null {
  const candidates = voices
    .filter((voice) => isVoiceForLanguage(voice, language))
    .sort((left, right) => {
      const qualityRank = (voice: Speech.Voice) =>
        voice.quality === Speech.VoiceQuality.Enhanced ? 0 : 1;
      return qualityRank(left) - qualityRank(right) || left.name.localeCompare(right.name);
    });

  return candidates[0] ?? null;
}

export function useSpeechPlayback({ latestTurn, selfLanguage }: UseSpeechPlaybackOptions) {
  const [autoplayEnabled, setAutoplayEnabled] = useState(true);
  const [ratePreset, setRatePreset] = useState<SpeechRatePreset>("normal");
  const [speakingTurnId, setSpeakingTurnId] = useState<string | null>(null);
  const [hasLoadedPreferences, setHasLoadedPreferences] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<Record<SupportedLanguage, Speech.Voice[]>>({
    ko: [],
    es: [],
  });
  const [selectedVoices, setSelectedVoices] = useState<Record<SupportedLanguage, Speech.Voice | null>>({
    ko: null,
    es: null,
  });
  const [preferredVoiceIds, setPreferredVoiceIds] = useState<SelectedVoiceIds>({
    ko: null,
    es: null,
  });
  const lastAutoPlayedTurnIdRef = useRef<string | null>(null);

  const stopSpeaking = useEffectEvent(async () => {
    await Speech.stop();
    setSpeakingTurnId(null);
  });

  const speakTurn = useEffectEvent(async (turn: ConversationTurn) => {
    if (!turn.translatedText.trim()) {
      return;
    }

    await Speech.stop();
    setSpeakingTurnId(turn.id);
    const playbackLanguage = selfLanguage ?? (turn.sourceLanguage === "ko" ? "es" : "ko");
    const selectedVoice = selectedVoices[playbackLanguage];
    Speech.speak(turn.translatedText, {
      language: speechLanguage(playbackLanguage),
      voice: selectedVoice?.identifier,
      pitch: 1.0,
      rate: speechRateValue(ratePreset),
      onDone: () => setSpeakingTurnId((current) => (current === turn.id ? null : current)),
      onStopped: () => setSpeakingTurnId((current) => (current === turn.id ? null : current)),
      onError: () => setSpeakingTurnId((current) => (current === turn.id ? null : current)),
    });
  });

  useEffect(() => {
    if (!latestTurn || !selfLanguage || !autoplayEnabled) {
      return;
    }

    if (lastAutoPlayedTurnIdRef.current === latestTurn.id) {
      return;
    }

    if (latestTurn.speaker.language === selfLanguage) {
      return;
    }

    lastAutoPlayedTurnIdRef.current = latestTurn.id;
    speakTurn(latestTurn);
  }, [autoplayEnabled, latestTurn, selfLanguage, speakTurn]);

  const cycleVoice = useEffectEvent((language: SupportedLanguage) => {
    const voices = availableVoices[language];
    if (voices.length === 0) {
      return;
    }

    setSelectedVoices((current) => {
      const currentVoice = current[language];
      const currentIndex = currentVoice
        ? voices.findIndex((voice) => voice.identifier === currentVoice.identifier)
        : -1;
      const nextVoice = voices[(currentIndex + 1) % voices.length] ?? null;
      setPreferredVoiceIds((voiceIds) => ({
        ...voiceIds,
        [language]: nextVoice?.identifier ?? null,
      }));
      return {
        ...current,
        [language]: nextVoice,
      };
    });
  });

  useEffect(() => {
    let isMounted = true;

    Speech.getAvailableVoicesAsync()
      .then((voices) => {
        if (!isMounted) {
          return;
        }

        const groupedVoices = {
          ko: voices.filter((voice) => isVoiceForLanguage(voice, "ko")),
          es: voices.filter((voice) => isVoiceForLanguage(voice, "es")),
        };
        setAvailableVoices(groupedVoices);
        const resolveVoice = (language: SupportedLanguage) =>
          groupedVoices[language].find((voice) => voice.identifier === preferredVoiceIds[language]) ??
          chooseInitialVoice(voices, language);
        setSelectedVoices({
          ko: resolveVoice("ko"),
          es: resolveVoice("es"),
        });
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }
        setAvailableVoices({ ko: [], es: [] });
        setSelectedVoices({ ko: null, es: null });
      });

    return () => {
      isMounted = false;
    };
  }, [preferredVoiceIds]);

  useEffect(() => {
    let isMounted = true;

    AsyncStorage.getItem(SPEECH_PREFERENCES_KEY)
      .then((stored) => {
        if (!stored || !isMounted) {
          return;
        }

        const parsed = JSON.parse(stored) as {
          autoplayEnabled?: boolean;
          ratePreset?: SpeechRatePreset;
          preferredVoiceIds?: SelectedVoiceIds;
        };

        if (typeof parsed.autoplayEnabled === "boolean") {
          setAutoplayEnabled(parsed.autoplayEnabled);
        }
        if (parsed.ratePreset === "slow" || parsed.ratePreset === "normal" || parsed.ratePreset === "fast") {
          setRatePreset(parsed.ratePreset);
        }
        if (parsed.preferredVoiceIds) {
          setPreferredVoiceIds({
            ko: parsed.preferredVoiceIds.ko ?? null,
            es: parsed.preferredVoiceIds.es ?? null,
          });
        }
      })
      .catch(() => {})
      .finally(() => {
        if (isMounted) {
          setHasLoadedPreferences(true);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!hasLoadedPreferences) {
      return;
    }

    const payload = JSON.stringify({
      autoplayEnabled,
      ratePreset,
      preferredVoiceIds: {
        ko: selectedVoices.ko?.identifier ?? preferredVoiceIds.ko ?? null,
        es: selectedVoices.es?.identifier ?? preferredVoiceIds.es ?? null,
      },
    });

    AsyncStorage.setItem(SPEECH_PREFERENCES_KEY, payload).catch(() => {});
  }, [autoplayEnabled, hasLoadedPreferences, preferredVoiceIds, ratePreset, selectedVoices]);

  useEffect(() => {
    return () => {
      stopSpeaking();
    };
  }, [stopSpeaking]);

  return {
    autoplayEnabled,
    availableVoiceCounts: {
      ko: availableVoices.ko.length,
      es: availableVoices.es.length,
    },
    cycleVoice,
    hasLoadedPreferences,
    ratePreset,
    selectedVoiceLabels: {
      ko: selectedVoices.ko?.name ?? "Default Korean voice",
      es: selectedVoices.es?.name ?? "Default Spanish voice",
    },
    setAutoplayEnabled,
    setRatePreset,
    speakTurn,
    speakingTurnId,
    stopSpeaking,
  };
}
