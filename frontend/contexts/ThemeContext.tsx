import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

import { darkColors, lightColors, type ThemeColors } from '@/constants/colors';

interface ThemeContextValue {
  isDark: boolean;
  colors: ThemeColors;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

// In-memory only for now (resets on app restart) — no persistence layer
// (AsyncStorage etc.) wired up yet.
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [isDark, setIsDark] = useState(false);

  const value = useMemo<ThemeContextValue>(
    () => ({
      isDark,
      colors: isDark ? darkColors : lightColors,
      toggleTheme: () => setIsDark((prev) => !prev),
    }),
    [isDark],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
