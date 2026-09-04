import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Platform,
  StyleSheet,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import Svg, { Path } from "react-native-svg";

import { Text } from "@/components/Text";
import type { ThemeColors } from "@/constants/colors";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { signInWithKakao } from "@/lib/kakaoAuth";

const BRAND_COLOR = "#2F6FED";
const KAKAO_YELLOW = "#FEE500";
const KAKAO_TEXT = "#1C1C1E";

function KakaoIcon() {
  return (
    <Svg width={18} height={18} viewBox="0 0 18 18" fill={KAKAO_TEXT}>
      <Path d="M9 1.5C4.3 1.5.5 4.5.5 8.1c0 2.3 1.6 4.3 3.9 5.5-.2.6-.7 2.5-.8 2.9 0 0-.02.1.05.16.07.05.16.02.16.02.2-.03 2.6-1.7 3.6-2.4.5.07 1.1.1 1.6.1 4.7 0 8.5-3 8.5-6.6S13.7 1.5 9 1.5z" />
    </Svg>
  );
}

export default function LoginScreen() {
  const { colors } = useTheme();
  const { login } = useAuth();
  const styles = useMemo(() => createStyles(colors), [colors]);
  const [isKakaoLoading, setIsKakaoLoading] = useState(false);

  const handleKakaoLogin = async () => {
    setIsKakaoLoading(true);
    try {
      const { accessToken } = await signInWithKakao();
      await login(accessToken);
    } catch (err) {
      Alert.alert(
        "카카오 로그인 실패",
        err instanceof Error ? err.message : "알 수 없는 오류가 발생했어요.",
      );
    } finally {
      setIsKakaoLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
      <View style={styles.center}>
        <View style={styles.logoBadge}>
          <Image
            source={require("@/assets/logo-without-font-transparent.png")}
            style={styles.wordmark}
            resizeMode="contain"
          />
        </View>
        <Image
          source={require("@/assets/logo-wordmark.png")}
          style={styles.wordmark}
          resizeMode="contain"
        />
        <Text style={styles.subtitle}>로그인하고 스크린샷을 정리해보세요</Text>
      </View>

      <View style={styles.bottom}>
        <TouchableOpacity
          style={styles.kakaoButton}
          onPress={handleKakaoLogin}
          disabled={isKakaoLoading}
          activeOpacity={0.85}
        >
          {isKakaoLoading ? (
            <ActivityIndicator color={KAKAO_TEXT} />
          ) : (
            <>
              <KakaoIcon />
              <Text weight="semiBold" style={styles.kakaoButtonText}>
                카카오로 계속하기
              </Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.push("/(auth)/login-email")}
          activeOpacity={0.6}
        >
          <Text weight="semiBold" style={styles.emailLoginText}>
            이메일로 로그인
          </Text>
        </TouchableOpacity>

        <Text style={styles.termsText}>
          계속하면 <Text style={styles.termsLink}>이용약관</Text> 및{" "}
          <Text style={styles.termsLink}>개인정보처리방침</Text>에 동의하게
          됩니다.
        </Text>
      </View>
    </SafeAreaView>
  );
}

function createStyles(colors: ThemeColors) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
      paddingHorizontal: 28,
    },
    center: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      gap: 16,
    },
    logoBadge: {
      width: 76,
      height: 76,
      borderRadius: 22,
      backgroundColor: colors.background,
      alignItems: "center",
      justifyContent: "center",
      ...Platform.select({
        ios: {
          shadowColor: BRAND_COLOR,
          shadowOffset: { width: 0, height: 8 },
          shadowOpacity: 0.28,
          shadowRadius: 20,
        },
        android: { elevation: 6 },
      }),
    },
    wordmark: {
      width: 168,
      height: 56,
    },
    subtitle: {
      fontSize: 14,
      color: colors.textMuted,
      marginTop: -8,
    },
    bottom: {
      gap: 11,
      paddingBottom: 24,
    },
    kakaoButton: {
      height: 52,
      borderRadius: 16,
      backgroundColor: KAKAO_YELLOW,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
    },
    kakaoButtonText: {
      fontSize: 16,
      color: KAKAO_TEXT,
    },
    emailLoginText: {
      textAlign: "center",
      fontSize: 14,
      color: colors.textMuted,
      paddingVertical: 4,
    },
    termsText: {
      textAlign: "center",
      fontSize: 13,
      color: colors.textPlaceholder,
      marginTop: 6,
    },
    termsLink: {
      fontSize: 13,
      color: colors.textMuted,
      textDecorationLine: "underline",
    },
  });
}
