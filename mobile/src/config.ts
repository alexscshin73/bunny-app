import { Platform } from "react-native";

export interface BackendPreset {
  label: string;
  url: string;
}

function inferDefaultBackendUrl(): string {
  const configured = process.env.EXPO_PUBLIC_BUNNY_BACKEND_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }

  if (Platform.OS === "android") {
    return "http://10.0.2.2:8000";
  }

  return "http://127.0.0.1:8000";
}

export const DEFAULT_BACKEND_URL = inferDefaultBackendUrl();

function uniquePresets(presets: BackendPreset[]): BackendPreset[] {
  const seen = new Set<string>();
  return presets.filter((preset) => {
    if (seen.has(preset.url)) {
      return false;
    }
    seen.add(preset.url);
    return true;
  });
}

export const BACKEND_PRESETS = uniquePresets([
  { label: "Configured", url: DEFAULT_BACKEND_URL },
  { label: "Localhost", url: "http://127.0.0.1:8000" },
  { label: "Android Emulator", url: "http://10.0.2.2:8000" },
]);

export const SUPPORTED_LANGUAGES = [
  { code: "ko", label: "Korean" },
  { code: "es", label: "Spanish" },
] as const;
