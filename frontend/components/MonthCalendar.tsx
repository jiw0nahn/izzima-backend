import { Ionicons } from '@expo/vector-icons';
import { useMemo } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { toLocalISODate } from '@/lib/date';

const WEEKDAY_LABELS = ['일', '월', '화', '수', '목', '금', '토'];

interface CalendarCell {
  date: Date;
  iso: string;
  isCurrentMonth: boolean;
  isToday: boolean;
  dotColor?: 'red' | 'blue';
}

function buildCells(
  viewedMonth: Date,
  dotColorForDate: (isoDate: string) => 'red' | 'blue' | undefined,
): CalendarCell[] {
  const year = viewedMonth.getFullYear();
  const month = viewedMonth.getMonth();
  const firstDayOfMonth = new Date(year, month, 1);
  const startWeekday = firstDayOfMonth.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const todayIso = toLocalISODate(new Date());

  const cells: CalendarCell[] = [];

  for (let i = 0; i < startWeekday; i++) {
    const date = new Date(year, month, i - startWeekday + 1);
    cells.push({
      date,
      iso: toLocalISODate(date),
      isCurrentMonth: false,
      isToday: false,
    });
  }
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const iso = toLocalISODate(date);
    cells.push({
      date,
      iso,
      isCurrentMonth: true,
      isToday: iso === todayIso,
      dotColor: dotColorForDate(iso),
    });
  }
  while (cells.length % 7 !== 0) {
    const previousDate = cells[cells.length - 1].date;
    const date = new Date(previousDate);
    date.setDate(date.getDate() + 1);
    cells.push({ date, iso: toLocalISODate(date), isCurrentMonth: false, isToday: false });
  }

  return cells;
}

export function MonthCalendar({
  viewedMonth,
  onChangeMonth,
  dotColorForDate,
  selectedDate,
  onSelectDate,
}: {
  viewedMonth: Date;
  onChangeMonth: (nextMonth: Date) => void;
  dotColorForDate: (isoDate: string) => 'red' | 'blue' | undefined;
  selectedDate: string;
  onSelectDate: (isoDate: string) => void;
}) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);
  const cells = buildCells(viewedMonth, dotColorForDate);
  const weeks: CalendarCell[][] = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }

  const goToMonth = (offset: number) => {
    onChangeMonth(new Date(viewedMonth.getFullYear(), viewedMonth.getMonth() + offset, 1));
  };

  const selectCell = (cell: CalendarCell) => {
    onSelectDate(cell.iso);
    if (!cell.isCurrentMonth) {
      onChangeMonth(new Date(cell.date.getFullYear(), cell.date.getMonth(), 1));
    }
  };

  return (
    <View>
      <View style={styles.monthRow}>
        <Text weight="extraBold" style={styles.monthLabel}>
          {viewedMonth.getFullYear()}년 {viewedMonth.getMonth() + 1}월
        </Text>
        <View style={styles.monthNav}>
          <Pressable style={styles.navButton} onPress={() => goToMonth(-1)} hitSlop={8}>
            <Ionicons name="chevron-back" size={18} color={colors.text} />
          </Pressable>
          <Pressable style={styles.navButton} onPress={() => goToMonth(1)} hitSlop={8}>
            <Ionicons name="chevron-forward" size={18} color={colors.text} />
          </Pressable>
        </View>
      </View>

      <View style={styles.weekdayRow}>
        {WEEKDAY_LABELS.map((label, index) => (
          <Text
            key={label}
            weight="semiBold"
            style={[
              styles.weekdayLabel,
              index === 0 && styles.sundayLabel,
              index === 6 && styles.saturdayLabel,
            ]}
          >
            {label}
          </Text>
        ))}
      </View>

      {weeks.map((week, weekIndex) => (
        <View key={weekIndex} style={styles.weekRow}>
          {week.map((cell) => {
            const isSelected = cell.iso === selectedDate;
            return (
              <Pressable key={cell.iso} style={styles.dayCell} onPress={() => selectCell(cell)} hitSlop={2}>
                <View
                  style={[
                    styles.dayCircle,
                    cell.isToday && styles.dayCircleToday,
                    isSelected && styles.dayCircleSelected,
                  ]}
                >
                  <Text
                    weight={cell.isToday || isSelected ? 'semiBold' : 'regular'}
                    style={[
                      styles.dayLabel,
                      !cell.isCurrentMonth && styles.dayLabelMuted,
                      isSelected && styles.dayLabelSelected,
                    ]}
                  >
                    {cell.date.getDate()}
                  </Text>
                </View>
                <View
                  style={[
                    styles.dot,
                    cell.dotColor === 'red' && styles.dotRed,
                    cell.dotColor === 'blue' && styles.dotBlue,
                  ]}
                />
              </Pressable>
            );
          })}
        </View>
      ))}
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    monthRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 12,
    },
    monthLabel: {
      fontSize: 20,
      color: colors.text,
    },
    monthNav: {
      flexDirection: 'row',
      gap: 4,
    },
    navButton: {
      width: 28,
      height: 28,
      borderRadius: 14,
      backgroundColor: colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
    },
    weekdayRow: {
      flexDirection: 'row',
    },
    weekdayLabel: {
      flex: 1,
      textAlign: 'center',
      fontSize: 13,
      color: colors.textMuted,
      marginBottom: 6,
    },
    sundayLabel: {
      color: '#EF4444',
    },
    saturdayLabel: {
      color: '#2F6FED',
    },
    weekRow: {
      flexDirection: 'row',
    },
    dayCell: {
      flex: 1,
      alignItems: 'center',
      paddingVertical: 4,
    },
    dayCircle: {
      width: 30,
      height: 30,
      borderRadius: 15,
      alignItems: 'center',
      justifyContent: 'center',
    },
    dayCircleToday: {
      backgroundColor: '#DBEAFE',
    },
    dayCircleSelected: {
      backgroundColor: '#2F6FED',
    },
    dayLabel: {
      fontSize: 14,
      color: colors.text,
    },
    dayLabelMuted: {
      color: colors.textPlaceholder,
    },
    dayLabelSelected: {
      color: '#FFFFFF',
    },
    dot: {
      width: 4,
      height: 4,
      borderRadius: 2,
      marginTop: 3,
    },
    dotRed: {
      backgroundColor: '#EF4444',
    },
    dotBlue: {
      backgroundColor: '#2F6FED',
    },
  });
