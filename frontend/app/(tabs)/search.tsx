import { Ionicons } from '@expo/vector-icons';
import { useMemo, useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Text } from '@/components/Text';
import { TextInput } from '@/components/TextInput';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

const SUGGESTED_QUERIES = ['안 쓴 쿠폰', '항공권', '영수증'];

export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.content}>
        <Text weight="extraBold" style={styles.title}>
          검색
        </Text>

        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color={colors.textMuted} />
          <TextInput
            style={styles.input}
            value={query}
            onChangeText={setQuery}
            placeholder="예: 지난달 카페에서 찍은 영수증"
          />
        </View>

        <View style={styles.suggestions}>
          {SUGGESTED_QUERIES.map((suggestion) => (
            <Pressable key={suggestion} style={styles.chip} onPress={() => setQuery(suggestion)}>
              <Text style={styles.chipLabel}>{suggestion}</Text>
            </Pressable>
          ))}
        </View>

        {query.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>검색어를 입력하거나</Text>
            <Text style={styles.emptyText}>추천 검색어를 선택해보세요</Text>
          </View>
        )}
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
    content: {
      flex: 1,
      paddingHorizontal: 20,
    },
    title: {
      fontSize: 32,
      color: colors.text,
      marginTop: 12,
      marginBottom: 20,
    },
    searchBar: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.surface,
      borderRadius: 12,
      paddingHorizontal: 14,
      height: 48,
      gap: 8,
    },
    input: {
      flex: 1,
      fontSize: 15,
      color: colors.text,
    },
    suggestions: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
      marginTop: 16,
    },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: 20,
      backgroundColor: colors.surface,
    },
    chipLabel: {
      fontSize: 14,
      color: colors.text,
    },
    emptyState: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      paddingBottom: 80,
    },
    emptyText: {
      fontSize: 14,
      color: colors.textMuted,
      textAlign: 'center',
      lineHeight: 20,
    },
  });
