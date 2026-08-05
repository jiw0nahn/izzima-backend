import { Ionicons } from '@expo/vector-icons';
import { useMemo } from 'react';
import { Modal, Pressable, StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import type { Category } from '@/types/home';

export function CategoryPickerSheet({
  visible,
  categories,
  selectedCategoryId,
  onSelect,
  onClose,
}: {
  visible: boolean;
  categories: Category[];
  selectedCategoryId: string;
  onSelect: (categoryId: string) => void;
  onClose: () => void;
}) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <View style={styles.sheet} onStartShouldSetResponder={() => true}>
          <Text weight="bold" style={styles.title}>
            카테고리 선택
          </Text>
          {categories.map((category, index) => {
            const isSelected = category.id === selectedCategoryId;
            return (
              <Pressable
                key={category.id}
                style={[styles.row, index === categories.length - 1 && styles.rowLast]}
                onPress={() => {
                  onSelect(category.id);
                  onClose();
                }}
              >
                <Text weight={isSelected ? 'semiBold' : 'regular'} style={styles.rowLabel}>
                  {category.name}
                </Text>
                {isSelected && <Ionicons name="checkmark" size={18} color="#2F6FED" />}
              </Pressable>
            );
          })}
        </View>
      </Pressable>
    </Modal>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    backdrop: {
      flex: 1,
      backgroundColor: 'rgba(17, 24, 39, 0.4)',
      justifyContent: 'flex-end',
    },
    sheet: {
      backgroundColor: colors.background,
      borderTopLeftRadius: 20,
      borderTopRightRadius: 20,
      paddingHorizontal: 20,
      paddingTop: 16,
      paddingBottom: 32,
    },
    title: {
      fontSize: 16,
      color: colors.text,
      marginBottom: 8,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: 14,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    rowLast: {
      borderBottomWidth: 0,
    },
    rowLabel: {
      fontSize: 15,
      color: colors.text,
    },
  });
