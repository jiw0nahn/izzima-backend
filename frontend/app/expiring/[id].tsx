import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { useMemo } from 'react';
import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge } from '@/components/Badge';
import { InfoRow } from '@/components/InfoRow';
import { TagList } from '@/components/TagList';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useFavorites } from '@/contexts/FavoritesContext';
import { useTheme } from '@/contexts/ThemeContext';
import { getBadgeVariant, getDDayLabel } from '@/lib/deadline';
import { DEADLINE_ITEMS } from '@/lib/mockData';
import { goBack } from '@/lib/navigation';

export default function ExpiringItemDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { isFavorite, toggleFavorite } = useFavorites();
  const favorited = isFavorite('expiring', id);
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  // Looks up the full deadline list (not just the "만료 임박" window) so this
  // screen also works when reached from the calendar's full event list.
  const item = DEADLINE_ITEMS.find((entry) => entry.id === id);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.topRow}>
          <Pressable style={styles.backButton} onPress={() => goBack()} hitSlop={8}>
            <Ionicons name="chevron-back" size={20} color="#2F6FED" />
            <Text weight="semiBold" style={styles.backLabel}>
              {item?.category ?? ''}
            </Text>
          </Pressable>
          <Pressable hitSlop={8} onPress={() => toggleFavorite('expiring', id)}>
            <Ionicons
              name={favorited ? 'star' : 'star-outline'}
              size={22}
              color={favorited ? '#F5A623' : colors.textMuted}
            />
          </Pressable>
        </View>

        <View style={styles.image}>
          {item ? (
            <View style={styles.imageTag}>
              <Text weight="semiBold" style={styles.imageTagLabel}>
                {item.category}
              </Text>
            </View>
          ) : null}
        </View>

        <View style={styles.titleRow}>
          <Text weight="extraBold" style={styles.title}>
            {item?.title ?? ''}
          </Text>
          {item ? <Badge label={getDDayLabel(item.daysLeft)} variant={getBadgeVariant(item.daysLeft)} /> : null}
        </View>

        {item ? (
          <View style={styles.tagListWrapper}>
            <TagList tags={item.tags} />
          </View>
        ) : null}

        <View style={styles.infoList}>
          <InfoRow label="카테고리" value={item?.category ?? ''} />
          <InfoRow label="날짜" value={item?.subtitle ?? ''} divider />
          {item?.location ? <InfoRow label="장소" value={item.location} divider /> : null}
        </View>

        <Pressable style={styles.calendarButton} onPress={() => router.push('/calendar')}>
          <Ionicons name="calendar" size={18} color="#fff" />
          <Text weight="semiBold" style={styles.calendarButtonLabel}>
            캘린더에서 보기
          </Text>
        </Pressable>
      </ScrollView>
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
    topRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 12,
      marginBottom: 12,
    },
    backButton: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    backLabel: {
      fontSize: 17,
      color: '#2F6FED',
      marginLeft: 2,
    },
    image: {
      height: 320,
      borderRadius: 20,
      backgroundColor: colors.surface,
      padding: 12,
    },
    imageTag: {
      alignSelf: 'flex-start',
      backgroundColor: 'rgba(17, 24, 39, 0.7)',
      paddingHorizontal: 10,
      paddingVertical: 5,
      borderRadius: 8,
    },
    imageTagLabel: {
      fontSize: 12,
      color: '#FFFFFF',
    },
    titleRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 20,
    },
    title: {
      flex: 1,
      fontSize: 22,
      color: colors.text,
      marginRight: 12,
    },
    tagListWrapper: {
      marginTop: 12,
    },
    infoList: {
      marginTop: 20,
    },
    calendarButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 8,
      backgroundColor: '#2F6FED',
      borderRadius: 14,
      paddingVertical: 16,
      marginTop: 24,
    },
    calendarButtonLabel: {
      fontSize: 16,
      color: '#FFFFFF',
    },
  });
