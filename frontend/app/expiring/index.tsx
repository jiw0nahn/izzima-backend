import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo } from 'react';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { DeadlineListRow } from '@/components/DeadlineListRow';
import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { goBack } from '@/lib/navigation';
import { EXPIRING_ITEMS } from '@/lib/mockData';

export default function ExpiringListScreen() {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.header}>
        <Pressable style={styles.backButton} onPress={() => goBack()} hitSlop={8}>
          <Ionicons name="chevron-back" size={20} color="#2F6FED" />
          <Text weight="semiBold" style={styles.backLabel}>
            홈
          </Text>
        </Pressable>
        <Text weight="extraBold" style={styles.title}>
          만료 임박
        </Text>
        <Text style={styles.subtitle}>{EXPIRING_ITEMS.length}건 · 임박순</Text>
      </View>

      <FlatList
        data={EXPIRING_ITEMS}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <Pressable onPress={() => router.push(`/expiring/${item.id}`)}>
            <DeadlineListRow item={item} />
          </Pressable>
        )}
        contentContainerStyle={styles.list}
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
  });
