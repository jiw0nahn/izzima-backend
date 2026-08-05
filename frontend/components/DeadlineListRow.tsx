import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { Badge } from '@/components/Badge';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { getBadgeVariant, getDDayLabel } from '@/lib/deadline';
import type { ExpiringItem } from '@/types/home';

export function DeadlineListRow({ item }: { item: ExpiringItem }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.card}>
      <View style={styles.thumbnail} />
      <View style={styles.textColumn}>
        <Text weight="semiBold" style={styles.title}>
          {item.title}
        </Text>
        <Text style={styles.subtitle}>
          {item.category} · {item.subtitle}
        </Text>
      </View>
      <Badge label={getDDayLabel(item.daysLeft)} variant={getBadgeVariant(item.daysLeft)} />
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    card: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.surface,
      borderRadius: 16,
      padding: 12,
      marginBottom: 12,
    },
    thumbnail: {
      width: 56,
      height: 56,
      borderRadius: 12,
      backgroundColor: colors.border,
      marginRight: 12,
    },
    textColumn: {
      flex: 1,
      marginRight: 8,
    },
    title: {
      fontSize: 16,
      color: colors.text,
    },
    subtitle: {
      fontSize: 13,
      color: colors.textMuted,
      marginTop: 4,
    },
  });
