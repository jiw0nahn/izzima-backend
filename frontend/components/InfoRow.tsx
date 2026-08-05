import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

export function InfoRow({
  label,
  value,
  divider = false,
}: {
  label: string;
  value: string;
  /** Show the top border used between stacked InfoRows. Skip it on the first row. */
  divider?: boolean;
}) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={[styles.row, divider && styles.rowDivider]}>
      <Text style={styles.label}>{label}</Text>
      <Text weight="semiBold" style={styles.value}>
        {value}
      </Text>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: 14,
    },
    rowDivider: {
      borderTopWidth: 1,
      borderTopColor: colors.border,
    },
    label: {
      fontSize: 14,
      color: colors.textMuted,
    },
    value: {
      fontSize: 14,
      color: colors.text,
    },
  });
