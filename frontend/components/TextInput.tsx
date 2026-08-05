import { TextInput as RNTextInput, type TextInputProps as RNTextInputProps } from 'react-native';

import { fontFamily } from '@/constants/fonts';
import { useTheme } from '@/contexts/ThemeContext';

export type TextInputProps = RNTextInputProps;

/**
 * Drop-in replacement for React Native's `TextInput` that defaults to the
 * app's Pretendard font, theme-aware text/placeholder color. `TextInput`
 * can't compose with `components/Text.tsx` (it's a separate native
 * primitive), so it gets its own small wrapper for the same reason.
 */
export function TextInput({ style, placeholderTextColor, ...props }: TextInputProps) {
  const { colors } = useTheme();
  return (
    <RNTextInput
      style={[{ fontFamily: fontFamily.regular, color: colors.text }, style]}
      placeholderTextColor={placeholderTextColor ?? colors.textMuted}
      {...props}
    />
  );
}
