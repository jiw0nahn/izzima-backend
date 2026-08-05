import { Ionicons } from "@expo/vector-icons";
import Feather from "@expo/vector-icons/Feather";
import Octicons from "@expo/vector-icons/Octicons";
import { router, Tabs } from "expo-router";
import { Pressable, StyleSheet, View } from "react-native";

import { fontFamily } from "@/constants/fonts";
import { useTheme } from "@/contexts/ThemeContext";

const ACTIVE_COLOR = "#2F6FED";
const INACTIVE_COLOR = "#9CA3AF";

// The "+" button opens the upload flow as a modal (see app/upload-modal.tsx)
// instead of switching to a normal tab panel, so it must not use the tab
// navigator's default press handling — it pushes the modal route directly.
// The modal itself is what prompts the user to pick screenshots from their
// gallery, so this button doesn't need to know about the picker at all.
function UploadTabButton() {
  return (
    <View style={styles.uploadButtonWrapper}>
      <Pressable
        style={styles.uploadButton}
        onPress={() => router.push("/upload-modal")}
      >
        <Ionicons name="add" size={28} color="#fff" />
      </Pressable>
    </View>
  );
}

export default function TabsLayout() {
  const { colors } = useTheme();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: ACTIVE_COLOR,
        tabBarInactiveTintColor: INACTIVE_COLOR,
        tabBarLabelStyle: { fontFamily: fontFamily.semiBold },
        tabBarStyle: {
          backgroundColor: colors.background,
          borderTopColor: colors.border,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "홈",
          tabBarIcon: ({ color, size }) => (
            <Feather name="home" color={color} size={22} />
          ),
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: "검색",
          tabBarIcon: ({ color, size }) => (
            <Feather name="search" color={color} size={22} />
          ),
        }}
      />
      <Tabs.Screen
        name="upload"
        options={{
          title: "",
          tabBarButton: () => <UploadTabButton />,
        }}
      />
      <Tabs.Screen
        name="calendar"
        options={{
          title: "캘린더",
          tabBarIcon: ({ color, size }) => (
            <Feather name="calendar" color={color} size={22} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "설정",
          tabBarIcon: ({ color, size }) => (
            <Feather name="user" color={color} size={22} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  uploadButtonWrapper: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  uploadButton: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: ACTIVE_COLOR,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 22,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
});
