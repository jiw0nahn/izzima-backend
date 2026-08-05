import { router, useLocalSearchParams } from 'expo-router';
import { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { CategoryPickerSheet } from '@/components/CategoryPickerSheet';
import { Text } from '@/components/Text';
import { UploadReviewRow } from '@/components/UploadReviewRow';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { CATEGORIES, classifyUpload } from '@/lib/mockData';
import type { UploadReviewItem } from '@/types/home';

export default function UploadReviewScreen() {
  const { uris: urisParam } = useLocalSearchParams<{ uris?: string }>();
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);
  const uris = useMemo<string[]>(() => {
    if (!urisParam) return [];
    try {
      return JSON.parse(urisParam) as string[];
    } catch {
      return [];
    }
  }, [urisParam]);

  const [items, setItems] = useState<UploadReviewItem[]>(() =>
    uris.map((uri, index) => ({
      id: `review-${index}`,
      uri,
      categoryId: classifyUpload(index).id,
    })),
  );
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const editingItem = items.find((item) => item.id === editingItemId) ?? null;

  const categoryNameById = (categoryId: string) =>
    CATEGORIES.find((category) => category.id === categoryId)?.name ?? '';

  const handleSelectCategory = (categoryId: string) => {
    if (!editingItemId) return;
    setItems((prev) => prev.map((item) => (item.id === editingItemId ? { ...item, categoryId } : item)));
  };

  // Closes the whole upload flow (picker + analysis + this review screen)
  // and drops the user back on whichever tab they started from.
  const finish = () => router.dismissAll();

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.header}>
        <Pressable onPress={finish} hitSlop={8}>
          <Text style={styles.cancelLabel}>취소</Text>
        </Pressable>
        <Text weight="semiBold" style={styles.headerTitle}>
          분류 확인
        </Text>
        <Pressable onPress={finish} hitSlop={8}>
          <Text weight="semiBold" style={styles.doneLabel}>
            완료
          </Text>
        </Pressable>
      </View>

      <Text style={styles.subtitle}>AI가 분류한 카테고리예요. 잘못됐다면 눌러서 바꿔주세요.</Text>

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <UploadReviewRow
            uri={item.uri}
            categoryName={categoryNameById(item.categoryId)}
            onChangeCategory={() => setEditingItemId(item.id)}
          />
        )}
      />

      <CategoryPickerSheet
        visible={editingItem !== null}
        categories={CATEGORIES}
        selectedCategoryId={editingItem?.categoryId ?? ''}
        onSelect={handleSelectCategory}
        onClose={() => setEditingItemId(null)}
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
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 20,
      marginTop: 12,
      paddingBottom: 8,
    },
    cancelLabel: {
      fontSize: 16,
      color: '#2F6FED',
    },
    headerTitle: {
      fontSize: 16,
      color: colors.text,
    },
    doneLabel: {
      fontSize: 16,
      color: '#2F6FED',
    },
    subtitle: {
      fontSize: 13,
      color: colors.textMuted,
      paddingHorizontal: 20,
      marginTop: 4,
      marginBottom: 16,
    },
    list: {
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
  });
