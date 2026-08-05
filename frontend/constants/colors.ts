// Semantic color tokens for light/dark mode. Only the colors that must flip
// between themes live here (screen background, primary/muted text, neutral
// surfaces used for cards/placeholders/dividers). Brand/accent colors (blue
// buttons, danger/info badges, tag pills) stay the same in both themes since
// they're self-contained (colored background + matching text), not dependent
// on the screen's base background.
export interface ThemeColors {
  background: string;
  surface: string;
  border: string;
  text: string;
  textMuted: string;
  textPlaceholder: string;
}

export const lightColors: ThemeColors = {
  background: '#FFFFFF',
  surface: '#F3F4F6',
  border: '#EEEEEE',
  text: '#111827',
  textMuted: '#9CA3AF',
  textPlaceholder: '#D1D5DB',
};

export const darkColors: ThemeColors = {
  background: '#0B0F17',
  surface: '#1C2333',
  border: '#2A3142',
  text: '#F3F4F6',
  textMuted: '#9CA3AF',
  textPlaceholder: '#4B5563',
};
