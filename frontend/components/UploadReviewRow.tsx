import { Ionicons } from '@expo/vector-icons';
import { useMemo } from 'react';
import { Image, Pressable, StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

export function UploadReviewRow({
  uri,
  categoryName,
  onChangeCategory,
}: {
  uri: string;
  categoryName: string;
  onChangeCategory: () => void;
}) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.row}>
      <Image source={{ uri }} style={styles.thumbnail} />
      <View style={styles.textColumn}>
        <Text style={styles.label}>자동 분류됨</Text>
        <Text weight="semiBold" style={styles.categoryName}>
          {categoryName}
        </Text>
      </View>
      <Pressable style={styles.changeButton} onPress={onChangeCategory} hitSlop={8}>
        <Text weight="semiBold" style={styles.changeButtonLabel}>
          변경
        </Text>
        <Ionicons name="chevron-forward" size={14} color="#2F6FED" />
      </Pressable>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    row: {
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
    },
    label: {
      fontSize: 12,
      color: colors.textMuted,
    },
    categoryName: {
      fontSize: 16,
      color: colors.text,
      marginTop: 2,
    },
    changeButton: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 2,
      paddingHorizontal: 8,
      paddingVertical: 6,
    },
    changeButtonLabel: {
      fontSize: 14,
      color: '#2F6FED',
    },
  });
