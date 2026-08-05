import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useMemo } from "react";
import { ScrollView, StyleSheet, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { CategoryCard } from "@/components/CategoryCard";
import { ExpiringItemCard } from "@/components/ExpiringItemCard";
import { Text } from "@/components/Text";
import type { ThemeColors } from "@/constants/colors";
import { useTheme } from "@/contexts/ThemeContext";
import { CATEGORIES, EXPIRING_ITEMS } from "@/lib/mockData";

export default function HomeScreen() {
  const { colors, isDark, toggleTheme } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.headerRow}>
          <View>
            <Text weight="bold" style={styles.title}>
              홈
            </Text>
            <Text style={styles.subtitle}>324개 자동 정리됨</Text>
          </View>
          <TouchableOpacity style={styles.iconButton} onPress={toggleTheme}>
            <Ionicons
              name={isDark ? "sunny-outline" : "moon-outline"}
              size={20}
              color={colors.textMuted}
            />
          </TouchableOpacity>
        </View>

        <View style={styles.sectionHeaderRow}>
          <Text weight="bold" style={styles.sectionTitle}>
            만료 임박
          </Text>
          <TouchableOpacity onPress={() => router.push("/expiring")}>
            <Text weight="semiBold" style={styles.sectionLink}>
              전체
            </Text>
          </TouchableOpacity>
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.expiringList}
        >
          {EXPIRING_ITEMS.map((item) => (
            <TouchableOpacity
              key={item.id}
              activeOpacity={0.7}
              onPress={() => router.push(`/expiring/${item.id}`)}
            >
              <ExpiringItemCard item={item} />
            </TouchableOpacity>
          ))}
        </ScrollView>

        <Text
          weight="bold"
          style={[styles.sectionTitle, styles.categorySectionTitle]}
        >
          카테고리
        </Text>
        <View style={styles.categoryGrid}>
          {CATEGORIES.map((category) => (
            <TouchableOpacity
              key={category.id}
              style={styles.categoryItem}
              activeOpacity={0.7}
              onPress={() => router.push(`/category/${category.id}`)}
            >
              <CategoryCard category={category} />
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
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
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
    headerRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
      marginTop: 12,
    },
    title: {
      fontSize: 32,
      color: colors.text,
    },
    subtitle: {
      fontSize: 14,
      color: colors.textMuted,
      marginTop: 4,
    },
    iconButton: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: colors.surface,
      alignItems: "center",
      justifyContent: "center",
    },
    sectionHeaderRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      marginTop: 28,
      marginBottom: 12,
    },
    sectionTitle: {
      fontSize: 20,
      color: colors.text,
    },
    sectionLink: {
      fontSize: 15,
      color: "#2F6FED",
    },
    expiringList: {
      gap: 12,
    },
    categorySectionTitle: {
      marginTop: 28,
      marginBottom: 14,
    },
    categoryGrid: {
      flexDirection: "row",
      flexWrap: "wrap",
      justifyContent: "space-between",
      rowGap: 20,
    },
    categoryItem: {
      width: "31%",
    },
  });
