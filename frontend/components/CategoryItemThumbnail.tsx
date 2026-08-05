import { Ionicons } from '@expo/vector-icons';
import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import type { CategoryItem } from '@/types/home';

export function CategoryItemThumbnail({ item }: { item: CategoryItem }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.thumbnail}>
      {item.status === 'used' && (
        <View style={styles.badge}>
          <Ionicons name="checkmark" size={12} color="#fff" />
        </View>
      )}
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    thumbnail: {
      width: '100%',
      aspectRatio: 3 / 4,
      borderRadius: 16,
      backgroundColor: colors.surface,
    },
    badge: {
      position: 'absolute',
      right: 8,
      bottom: 8,
      width: 20,
      height: 20,
      borderRadius: 10,
      backgroundColor: 'rgba(17, 24, 39, 0.6)',
      alignItems: 'center',
      justifyContent: 'center',
    },
  });
