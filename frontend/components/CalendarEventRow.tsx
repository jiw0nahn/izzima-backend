import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { getDDayLabel, isUrgent } from '@/lib/deadline';
import type { ExpiringItem } from '@/types/home';

export function CalendarEventRow({ event }: { event: ExpiringItem }) {
  const urgent = isUrgent(event.daysLeft);
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.row}>
      <View style={[styles.bar, urgent ? styles.barUrgent : styles.barNormal]} />
      <View style={styles.thumbnail} />
      <View style={styles.textColumn}>
        <Text weight="semiBold" style={styles.title}>
          {event.title}
        </Text>
        <Text style={styles.subtitle}>{event.subtitle}</Text>
      </View>
      <Text weight="bold" style={[styles.dDay, urgent && styles.dDayUrgent]}>
        {getDDayLabel(event.daysLeft)}
      </Text>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    row: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: 10,
    },
    bar: {
      width: 3,
      height: 36,
      borderRadius: 2,
      marginRight: 10,
    },
    barUrgent: {
      backgroundColor: '#EF4444',
    },
    barNormal: {
      backgroundColor: '#2F6FED',
    },
    thumbnail: {
      width: 44,
      height: 44,
      borderRadius: 10,
      backgroundColor: colors.surface,
      marginRight: 12,
    },
    textColumn: {
      flex: 1,
    },
    title: {
      fontSize: 15,
      color: colors.text,
    },
    subtitle: {
      fontSize: 13,
      color: colors.textMuted,
      marginTop: 2,
    },
    dDay: {
      fontSize: 14,
      color: colors.text,
    },
    dDayUrgent: {
      color: '#EF4444',
    },
  });
