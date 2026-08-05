import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { CalendarEventRow } from '@/components/CalendarEventRow';
import { MonthCalendar } from '@/components/MonthCalendar';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { toLocalISODate } from '@/lib/date';
import { isUrgent } from '@/lib/deadline';
import { CALENDAR_EVENTS } from '@/lib/mockData';

function dotColorForDate(isoDate: string): 'red' | 'blue' | undefined {
  const eventsOnDate = CALENDAR_EVENTS.filter((event) => event.date === isoDate);
  if (eventsOnDate.length === 0) return undefined;
  return eventsOnDate.some((event) => isUrgent(event.daysLeft)) ? 'red' : 'blue';
}

function formatSelectedDateLabel(isoDate: string): string {
  const [, month, day] = isoDate.split('-');
  return `${Number(month)}월 ${Number(day)}일`;
}

export default function CalendarScreen() {
  const [viewedMonth, setViewedMonth] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [selectedDate, setSelectedDate] = useState(() => toLocalISODate(new Date()));
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  const eventsOnSelectedDate = useMemo(
    () => CALENDAR_EVENTS.filter((event) => event.date === selectedDate),
    [selectedDate],
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <FlatList
        data={eventsOnSelectedDate}
        keyExtractor={(event) => event.id}
        renderItem={({ item }) => (
          <Pressable onPress={() => router.push(`/expiring/${item.id}`)}>
            <CalendarEventRow event={item} />
          </Pressable>
        )}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          <View>
            <Text weight="extraBold" style={styles.title}>
              일정
            </Text>
            <MonthCalendar
              viewedMonth={viewedMonth}
              onChangeMonth={setViewedMonth}
              dotColorForDate={dotColorForDate}
              selectedDate={selectedDate}
              onSelectDate={setSelectedDate}
            />
            <Text style={styles.eventCountLabel}>
              {formatSelectedDateLabel(selectedDate)} 일정 {eventsOnSelectedDate.length}건
            </Text>
          </View>
        }
        ListEmptyComponent={<Text style={styles.emptyLabel}>이 날짜에는 일정이 없어요</Text>}
      />
    </SafeAreaView>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    content: {
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
    title: {
      fontSize: 32,
      color: colors.text,
      marginTop: 12,
      marginBottom: 20,
    },
    eventCountLabel: {
      fontSize: 14,
      color: colors.textMuted,
      marginTop: 24,
      marginBottom: 8,
    },
    emptyLabel: {
      fontSize: 14,
      color: colors.textMuted,
      textAlign: 'center',
      paddingVertical: 32,
    },
  });
