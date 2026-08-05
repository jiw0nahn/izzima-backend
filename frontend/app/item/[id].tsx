import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { useMemo } from 'react';
import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { InfoRow } from '@/components/InfoRow';
import { TagList } from '@/components/TagList';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useFavorites } from '@/contexts/FavoritesContext';
import { useTheme } from '@/contexts/ThemeContext';
import { CATEGORY_ITEMS } from '@/lib/mockData';
import { goBack } from '@/lib/navigation';

export default function ItemDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { isFavorite, toggleFavorite } = useFavorites();
  const favorited = isFavorite('category-item', id);
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  const item = CATEGORY_ITEMS.find((entry) => entry.id === id);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.topRow}>
          <Pressable style={styles.backButton} onPress={() => goBack()} hitSlop={8}>
            <Ionicons name="chevron-back" size={20} color="#2F6FED" />
            <Text weight="semiBold" style={styles.backLabel}>
              {item?.categoryName ?? ''}
            </Text>
          </Pressable>
          <Pressable hitSlop={8} onPress={() => toggleFavorite('category-item', id)}>
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
                {item.categoryName}
              </Text>
            </View>
          ) : null}
        </View>

        <Text weight="extraBold" style={styles.title}>
          {item?.title ?? ''}
        </Text>

        {item ? (
          <View style={styles.tagListWrapper}>
            <TagList tags={item.tags} />
          </View>
        ) : null}

        <View style={styles.infoList}>
          <InfoRow label="카테고리" value={item?.categoryName ?? ''} />
          <InfoRow label="날짜" value={item?.savedAtLabel ?? ''} divider />
        </View>

        {!item?.scheduleDetected && (
          <Text style={styles.noScheduleText}>이 스크린샷에서 일정이 감지되지 않았어요</Text>
        )}
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
    title: {
      fontSize: 22,
      color: colors.text,
      marginTop: 20,
    },
    tagListWrapper: {
      marginTop: 12,
    },
    infoList: {
      marginTop: 20,
    },
    noScheduleText: {
      marginTop: 24,
      fontSize: 13,
      color: colors.textMuted,
      textAlign: 'center',
    },
  });
