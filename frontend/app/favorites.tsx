import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo } from 'react';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { FavoriteRow } from '@/components/FavoriteRow';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useFavorites } from '@/contexts/FavoritesContext';
import { useTheme } from '@/contexts/ThemeContext';
import { CATEGORY_ITEMS, DEADLINE_ITEMS } from '@/lib/mockData';
import { goBack } from '@/lib/navigation';

interface FavoriteRowData {
  key: string;
  title: string;
  subtitle: string;
  onPress: () => void;
}

export default function FavoritesScreen() {
  const { favorites } = useFavorites();
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  // Favorited ids come from two unrelated mock arrays (see FavoriteKind) —
  // resolve each entry against the right one and drop it silently if the
  // underlying item is somehow gone (shouldn't happen with mock data, but
  // keeps this screen safe once real deletable data exists).
  const rows = useMemo<FavoriteRowData[]>(() => {
    return favorites
      .map((entry): FavoriteRowData | null => {
        if (entry.kind === 'expiring') {
          const item = DEADLINE_ITEMS.find((candidate) => candidate.id === entry.id);
          if (!item) return null;
          return {
            key: `expiring-${item.id}`,
            title: item.title,
            subtitle: `${item.category} · ${item.subtitle}`,
            onPress: () => router.push(`/expiring/${item.id}`),
          };
        }
        const item = CATEGORY_ITEMS.find((candidate) => candidate.id === entry.id);
        if (!item) return null;
        return {
          key: `item-${item.id}`,
          title: item.title,
          subtitle: item.categoryName,
          onPress: () => router.push(`/item/${item.id}`),
        };
      })
      .filter((row): row is FavoriteRowData => row !== null);
  }, [favorites]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.header}>
        <Pressable style={styles.backButton} onPress={() => goBack()} hitSlop={8}>
          <Ionicons name="chevron-back" size={20} color="#2F6FED" />
          <Text weight="semiBold" style={styles.backLabel}>
            설정
          </Text>
        </Pressable>
        <Text weight="extraBold" style={styles.title}>
          즐겨찾기
        </Text>
        <Text style={styles.subtitle}>{rows.length}건</Text>
      </View>

      <FlatList
        data={rows}
        keyExtractor={(row) => row.key}
        renderItem={({ item }) => (
          <FavoriteRow title={item.title} subtitle={item.subtitle} onPress={item.onPress} />
        )}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <Text style={styles.emptyLabel}>
            즐겨찾기한 이미지가 없어요{'\n'}상세 화면에서 별표를 눌러 추가해보세요
          </Text>
        }
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
    header: {
      paddingHorizontal: 20,
      marginTop: 12,
    },
    backButton: {
      flexDirection: 'row',
      alignItems: 'center',
      alignSelf: 'flex-start',
      marginBottom: 8,
    },
    backLabel: {
      fontSize: 17,
      color: '#2F6FED',
      marginLeft: 2,
    },
    title: {
      fontSize: 28,
      color: colors.text,
    },
    subtitle: {
      fontSize: 14,
      color: colors.textMuted,
      marginTop: 4,
      marginBottom: 16,
    },
    list: {
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
    emptyLabel: {
      fontSize: 14,
      color: colors.textMuted,
      textAlign: 'center',
      lineHeight: 20,
      paddingVertical: 48,
    },
  });
