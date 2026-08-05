import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';
import { CURRENT_USER } from '@/lib/mockData';

export default function SettingsScreen() {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.container}>
        <Text weight="extraBold" style={styles.title}>
          설정
        </Text>

        <View style={styles.profileRow}>
          <View style={styles.avatar}>
            <Ionicons name="person" size={24} color={colors.textMuted} />
          </View>
          <Text weight="bold" style={styles.nickname}>
            {CURRENT_USER.nickname}님
          </Text>
        </View>

        <View style={styles.menu}>
          <Pressable style={styles.menuRow} onPress={() => router.push('/favorites')}>
            <Ionicons name="star-outline" size={20} color={colors.text} />
            <Text style={styles.menuLabel}>즐겨찾기</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
      backgroundColor: colors.background,
      paddingHorizontal: 20,
    },
    title: {
      fontSize: 32,
      color: colors.text,
      marginTop: 12,
    },
    profileRow: {
      flexDirection: 'row',
      alignItems: 'center',
      marginTop: 28,
      marginBottom: 28,
    },
    avatar: {
      width: 52,
      height: 52,
      borderRadius: 26,
      backgroundColor: colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
      marginRight: 12,
    },
    nickname: {
      fontSize: 18,
      color: colors.text,
    },
    menu: {
      borderTopWidth: 1,
      borderTopColor: colors.border,
    },
    menuRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
      paddingVertical: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    menuLabel: {
      flex: 1,
      fontSize: 15,
      color: colors.text,
    },
  });
