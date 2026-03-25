import { Platform } from "react-native";

export const palette = {
  canvas: "#f5eddc",
  panel: "#fff9ef",
  panelAlt: "#efe3cf",
  ink: "#1d1a17",
  inkSoft: "#5f564c",
  accent: "#d96a3a",
  accentDeep: "#9f3d1f",
  line: "#d8c5aa",
  success: "#22624f",
  warning: "#7f4c1f",
  shadow: "rgba(68, 40, 16, 0.12)",
};

export const typography = {
  display: Platform.select({
    ios: "Georgia",
    android: "serif",
    default: "serif",
  }),
  body: Platform.select({
    ios: "Avenir Next",
    android: "sans-serif-medium",
    default: "sans-serif",
  }),
  mono: Platform.select({
    ios: "Menlo",
    android: "monospace",
    default: "monospace",
  }),
};
