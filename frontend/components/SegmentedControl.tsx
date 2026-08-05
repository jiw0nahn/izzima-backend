import { useMemo } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

export interface SegmentedControlOption<T extends string> {
  label: string;
  value: T;
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
}: {
  options: SegmentedControlOption<T>[];
  value: T;
  onChange: (value: T) => void;
}) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.container}>
      {options.map((option) => {
        const isActive = option.value === value;
        return (
          <Pressable
            key={option.value}
            style={[styles.segment, isActive && styles.segmentActive]}
            onPress={() => onChange(option.value)}
          >
            <Text
              weight={isActive ? 'semiBold' : 'regular'}
              style={[styles.label, isActive && styles.labelActive]}
            >
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    container: {
      flexDirection: 'row',
      backgroundColor: colors.surface,
      borderRadius: 12,
      padding: 4,
    },
    segment: {
      flex: 1,
      paddingVertical: 8,
      borderRadius: 9,
      alignItems: 'center',
    },
    segmentActive: {
      backgroundColor: colors.background,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.08,
      shadowRadius: 2,
      elevation: 1,
    },
    label: {
      fontSize: 14,
      color: colors.textMuted,
    },
    labelActive: {
      color: colors.text,
    },
  });
