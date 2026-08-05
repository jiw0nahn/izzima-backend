import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { Badge } from '@/components/Badge';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { getBadgeVariant, getDDayLabel } from '@/lib/deadline';
import type { ExpiringItem } from '@/types/home';

export function ExpiringItemCard({ item }: { item: ExpiringItem }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.category}>{item.category}</Text>
        <Badge label={getDDayLabel(item.daysLeft)} variant={getBadgeVariant(item.daysLeft)} />
      </View>
      <View style={styles.thumbnail} />
      <Text weight="bold" style={styles.title}>
        {item.title}
      </Text>
      <Text style={styles.subtitle}>{item.subtitle}</Text>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    card: {
      width: 180,
      padding: 12,
      borderRadius: 16,
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: colors.background,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    category: {
      fontSize: 13,
      color: colors.textMuted,
    },
    thumbnail: {
      height: 110,
      borderRadius: 12,
      backgroundColor: colors.surface,
      marginVertical: 10,
    },
    title: {
      fontSize: 15,
      color: colors.text,
      marginBottom: 2,
    },
    subtitle: {
      fontSize: 13,
      color: colors.textMuted,
    },
  });
