import { useMemo } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

export function TagList({ tags, onAddTag }: { tags: string[]; onAddTag?: () => void }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.row}>
      {tags.map((tag) => (
        <View key={tag} style={styles.tag}>
          <Text weight="semiBold" style={styles.tagLabel}>
            {tag}
          </Text>
        </View>
      ))}
      <Pressable style={styles.addTag} onPress={onAddTag}>
        <Text style={styles.addTagLabel}>+ 태그</Text>
      </Pressable>
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    row: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    tag: {
      backgroundColor: '#DBEAFE',
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
    },
    tagLabel: {
      fontSize: 13,
      color: '#2563EB',
    },
    addTag: {
      borderWidth: 1,
      borderColor: colors.textPlaceholder,
      borderStyle: 'dashed',
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
    },
    addTagLabel: {
      fontSize: 13,
      color: colors.textMuted,
    },
  });
