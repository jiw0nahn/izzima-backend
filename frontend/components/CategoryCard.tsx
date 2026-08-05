import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import type { Category } from '@/types/home';

export function CategoryCard({ category }: { category: Category }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.wrapper}>
      <View style={styles.thumbnail}>
        <View style={styles.grid}>
          {Array.from({ length: 4 }).map((_, index) => (
            <View key={index} style={styles.cell} />
          ))}
        </View>
      </View>
      <Text weight="bold" style={styles.name}>
        {category.name}
      </Text>
      <Text style={styles.count}>{category.count}</Text>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    wrapper: {
      width: '100%',
    },
    thumbnail: {
      aspectRatio: 1,
      borderRadius: 16,
      borderWidth: 1,
      borderColor: colors.border,
      padding: 10,
      justifyContent: 'center',
    },
    grid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 6,
    },
    cell: {
      width: '45%',
      aspectRatio: 1,
      borderRadius: 6,
      backgroundColor: colors.surface,
    },
    name: {
      marginTop: 8,
      fontSize: 14,
      color: colors.text,
    },
    count: {
      fontSize: 13,
      color: colors.textMuted,
      marginTop: 2,
    },
  });
