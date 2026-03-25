import {
  PermissionStatus,
  RecordingPresets,
  requestRecordingPermissionsAsync,
  setAudioModeAsync,
  useAudioRecorder,
  useAudioRecorderState,
} from "expo-audio";
import { Platform } from "react-native";
import { useEffect, useEffectEvent, useMemo, useRef, useState } from "react";

import { SupportedLanguage } from "../types";

type MicrophoneMode = "idle" | "preparing" | "streaming" | "recording_only" | "error";

interface UseMicrophoneBridgeOptions {
  canStream: boolean;
  language: SupportedLanguage;
  onNativeRecordingReady: (fileUri: string) => Promise<unknown>;
  onSendAudioChunk: (chunk: ArrayBuffer) => boolean;
  onStartSession: (sampleRate: number, language: SupportedLanguage) => void;
  onStopSession: () => void;
}

interface WebCaptureState {
  audioContext: AudioContext;
  sourceNode: MediaStreamAudioSourceNode;
  processorNode: ScriptProcessorNode;
  mediaStream: MediaStream;
}

interface BrowserWindowWithWebkitAudioContext extends Window {
  webkitAudioContext?: typeof AudioContext;
}

const NATIVE_RECORDING_OPTIONS = {
  ...RecordingPresets.HIGH_QUALITY,
  isMeteringEnabled: true,
  sampleRate: 16000,
  numberOfChannels: 1,
  bitRate: 64000,
};

function floatToPcm16Buffer(input: Float32Array): ArrayBuffer {
  const buffer = new ArrayBuffer(input.length * 2);
  const view = new DataView(buffer);

  for (let index = 0; index < input.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, input[index]));
    view.setInt16(index * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
  }

  return buffer;
}

export function useMicrophoneBridge({
  canStream,
  language,
  onNativeRecordingReady,
  onSendAudioChunk,
  onStartSession,
  onStopSession,
}: UseMicrophoneBridgeOptions) {
  const recorder = useAudioRecorder(NATIVE_RECORDING_OPTIONS);
  const recorderState = useAudioRecorderState(recorder, 250);
  const webCaptureRef = useRef<WebCaptureState | null>(null);
  const [mode, setMode] = useState<MicrophoneMode>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<PermissionStatus | "unknown">("unknown");

  const stopWebCapture = useEffectEvent(async () => {
    const current = webCaptureRef.current;
    if (!current) {
      return;
    }

    current.processorNode.disconnect();
    current.sourceNode.disconnect();
    current.mediaStream.getTracks().forEach((track) => track.stop());
    await current.audioContext.close();
    webCaptureRef.current = null;
  });

  const stopNativeRecorder = useEffectEvent(async () => {
    if (recorderState.isRecording) {
      await recorder.stop();
    }
    const fileUri = recorder.uri ?? recorder.getStatus().url;
    if (fileUri) {
      await onNativeRecordingReady(fileUri);
      setMessage("Uploaded recorded audio for translation.");
    } else {
      setMessage("Recording stopped, but no local audio file was available to upload.");
    }
  });

  const stop = useEffectEvent(async () => {
    if (Platform.OS === "web") {
      await stopWebCapture();
      if (mode === "streaming") {
        onStopSession();
      }
    } else {
      await stopNativeRecorder();
    }

    await setAudioModeAsync({
      allowsRecording: false,
      interruptionMode: "mixWithOthers",
      playsInSilentMode: true,
      shouldPlayInBackground: false,
      shouldRouteThroughEarpiece: false,
    });
    setMode("idle");
  });

  const start = useEffectEvent(async () => {
    setMessage(null);
    setMode("preparing");

    const permission = await requestRecordingPermissionsAsync();
    setPermissionStatus(permission.status);

    if (!permission.granted) {
      setMode("error");
      setMessage("Microphone permission was denied.");
      return;
    }

    await setAudioModeAsync({
      allowsRecording: true,
      interruptionMode: "mixWithOthers",
      playsInSilentMode: true,
      shouldPlayInBackground: false,
      shouldRouteThroughEarpiece: false,
    });

    if (Platform.OS === "web") {
      if (!canStream) {
        setMode("error");
        setMessage("Connect to a room before starting microphone streaming.");
        return;
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      const browserWindow = window as BrowserWindowWithWebkitAudioContext;
      const AudioContextCtor = globalThis.AudioContext || browserWindow.webkitAudioContext;
      const audioContext = new AudioContextCtor();
      const sourceNode = audioContext.createMediaStreamSource(mediaStream);
      const processorNode = audioContext.createScriptProcessor(2048, 1, 1);

      onStartSession(audioContext.sampleRate, language);

      processorNode.onaudioprocess = (event: AudioProcessingEvent) => {
        if (!canStream) {
          return;
        }

        const channelData = event.inputBuffer.getChannelData(0);
        const pcmBuffer = floatToPcm16Buffer(channelData);
        const sent = onSendAudioChunk(pcmBuffer);
        if (!sent) {
          setMessage("Audio chunk dropped because the realtime socket is not ready.");
        }
      };

      sourceNode.connect(processorNode);
      processorNode.connect(audioContext.destination);
      webCaptureRef.current = {
        audioContext,
        mediaStream,
        processorNode,
        sourceNode,
      };

      setMode("streaming");
      setMessage("Web microphone is streaming PCM chunks to the realtime room.");
      return;
    }

    await recorder.prepareToRecordAsync();
    recorder.record();
    setMode("recording_only");
    setMessage(
      "Native Expo recording is active. The official expo-audio API exposes recorder status and files, but not realtime microphone PCM callbacks on iOS/Android."
    );
  });

  useEffect(() => {
    if (!canStream && mode === "streaming") {
      stop();
    }
  }, [canStream, mode, stop]);

  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  const statusLine = useMemo(() => {
    if (mode === "streaming") {
      return "Streaming live microphone audio";
    }
    if (mode === "recording_only") {
      return "Recording locally on device";
    }
    if (mode === "preparing") {
      return "Preparing microphone";
    }
    if (mode === "error") {
      return "Microphone error";
    }
    return "Microphone idle";
  }, [mode]);

  return {
    durationMillis: recorderState.durationMillis,
    isActive: mode === "streaming" || mode === "recording_only",
    message,
    metering: recorderState.metering,
    mode,
    permissionStatus,
    start,
    statusLine,
    stop,
  };
}
