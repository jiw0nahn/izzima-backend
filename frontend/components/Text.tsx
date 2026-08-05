import { Text as RNText, type TextProps as RNTextProps } from 'react-native';

import { fontFamily, type FontWeightToken } from '@/constants/fonts';
import { useTheme } from '@/contexts/ThemeContext';

export interface TextProps extends RNTextProps {
  /** Pretendard weight to render with. Defaults to regular. */
  weight?: FontWeightToken;
}

/**
 * Drop-in replacement for React Native's `Text` that renders with the app's
 * Pretendard font and the current theme's default text color. Pass an
 * explicit `color` in `style` to override (e.g. muted/danger/brand text) —
 * it still wins since it's applied after this default.
 */
export function Text({ weight = 'regular', style, ...props }: TextProps) {
  const { colors } = useTheme();
  return <RNText style={[{ fontFamily: fontFamily[weight], color: colors.text }, style]} {...props} />;
}
