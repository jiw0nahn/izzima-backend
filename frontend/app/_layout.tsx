import { useFonts } from "expo-font";
import { Redirect, Stack, useSegments } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { FavoritesProvider } from "@/contexts/FavoritesContext";
import { ThemeProvider, useTheme } from "@/contexts/ThemeContext";

function RootNavigator() {
  const { isDark } = useTheme();
  const { isLoading, isLoggedIn } = useAuth();
  const segments = useSegments();

  if (isLoading) {
    return null;
  }

  const inAuthGroup = segments[0] === "(auth)";

  return (
    <>
      <StatusBar style={isDark ? "light" : "dark"} />
      <Stack screenOptions={{ headerShown: false }} initialRouteName={isLoggedIn ? "(tabs)" : "(auth)"}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="upload-modal" options={{ presentation: "modal" }} />
      </Stack>
      {!isLoggedIn && !inAuthGroup && <Redirect href="/(auth)/onboarding" />}
      {isLoggedIn && inAuthGroup && <Redirect href="/(tabs)" />}
    </>
  );
}

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    "Pretendard-Regular": require("../assets/fonts/Pretendard-Regular.otf"),
    "Pretendard-SemiBold": require("../assets/fonts/Pretendard-SemiBold.otf"),
    "Pretendard-Bold": require("../assets/fonts/Pretendard-Bold.otf"),
    "Pretendard-ExtraBold": require("../assets/fonts/Pretendard-ExtraBold.otf"),
  });

  if (!fontsLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthProvider>
          <FavoritesProvider>
            <RootNavigator />
          </FavoritesProvider>
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
