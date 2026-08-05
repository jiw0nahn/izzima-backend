import { Ionicons } from '@expo/vector-icons';
import { router, useLocalSearchParams } from 'expo-router';
import { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { CategoryItemThumbnail } from '@/components/CategoryItemThumbnail';
import { SegmentedControl, type SegmentedControlOption } from '@/components/SegmentedControl';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { CATEGORIES, CATEGORY_ITEMS } from '@/lib/mockData';
import { goBack } from '@/lib/navigation';
import type { CategoryFilter } from '@/types/home';

const FILTERS: SegmentedControlOption<CategoryFilter>[] = [
  { label: '전체', value: 'all' },
  { label: '임박', value: 'expiring' },
  { label: '사용완료', value: 'used' },
];

export default function CategoryDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [filter, setFilter] = useState<CategoryFilter>('all');
  // "선택" only toggles the button label for now — multi-select wasn't specced
  // in the wireframe beyond this button, so there's no selection UI yet.
  const [selectionMode, setSelectionMode] = useState(false);
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  const category = CATEGORIES.find((item) => item.id === id);
  const items = useMemo(() => {
    const categoryItems = CATEGORY_ITEMS.filter((item) => item.categoryId === id);
    return filter === 'all' ? categoryItems : categoryItems.filter((item) => item.status === filter);
  }, [id, filter]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.header}>
        <View style={styles.topRow}>
          <Pressable style={styles.backButton} onPress={() => goBack()} hitSlop={8}>
            <Ionicons name="chevron-back" size={20} color="#2F6FED" />
            <Text weight="semiBold" style={styles.backLabel}>
              홈
            </Text>
          </Pressable>
          <Pressable hitSlop={8} onPress={() => setSelectionMode((prev) => !prev)}>
            <Text weight="semiBold" style={styles.selectLabel}>
              {selectionMode ? '완료' : '선택'}
            </Text>
          </Pressable>
        </View>
        <Text weight="extraBold" style={styles.title}>
          {category?.name ?? ''}
        </Text>
        <Text style={styles.subtitle}>{category?.count ?? 0}장 · 최근순</Text>
      </View>

      <View style={styles.segmentedControlWrapper}>
        <SegmentedControl options={FILTERS} value={filter} onChange={setFilter} />
      </View>

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        numColumns={3}
        columnWrapperStyle={styles.row}
        contentContainerStyle={styles.grid}
        renderItem={({ item }) => (
          <Pressable style={styles.thumbnailWrapper} onPress={() => router.push(`/item/${item.id}`)}>
            <CategoryItemThumbnail item={item} />
          </Pressable>
        )}
        showsVerticalScrollIndicator={false}
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
    topRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 8,
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
    selectLabel: {
      fontSize: 15,
      color: '#2F6FED',
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
    segmentedControlWrapper: {
      paddingHorizontal: 20,
      marginBottom: 16,
    },
    grid: {
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
    row: {
      justifyContent: 'space-between',
      marginBottom: 12,
    },
    thumbnailWrapper: {
      width: '31%',
    },
  });
