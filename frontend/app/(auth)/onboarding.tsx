import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Text } from '@/components/Text';
import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

const BRAND_COLOR = '#2F6FED';

interface OnboardingStep {
  bg: string;
  iconColor: string;
  iconName: keyof typeof Ionicons.glyphMap;
  title: string;
  description: string;
  cta: string;
}

const STEPS: OnboardingStep[] = [
  {
    bg: '#E8F2FF',
    iconColor: '#0A84FF',
    iconName: 'images-outline',
    title: '스크린샷을 자동으로 정리해요',
    description: '카메라 롤에 쌓인 스크린샷을 앱이 알아서 분류하고 보관해요.',
    cta: '다음',
  },
  {
    bg: '#FFF1E0',
    iconColor: '#FF9500',
    iconName: 'alarm-outline',
    title: '만료 임박 알림을 받아요',
    description: '기한이 다가오는 쿠폰, 티켓, 예약을 미리 알려드려요.',
    cta: '다음',
  },
  {
    bg: '#E9F9F0',
    iconColor: '#34C759',
    iconName: 'grid-outline',
    title: '카테고리별로 모아봐요',
    description: '쿠폰, 예약, 메모, 링크까지 한눈에 찾을 수 있어요.',
    cta: '시작하기',
  },
];

const finishOnboarding = () => router.replace('/(auth)/login');

export default function OnboardingScreen() {
  const { colors } = useTheme();
  const [stepIndex, setStepIndex] = useState(0);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      finishOnboarding();
    } else {
      setStepIndex((prev) => prev + 1);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'bottom']}>
      <View style={styles.skipRow}>
        <TouchableOpacity onPress={finishOnboarding}>
          <Text style={styles.skipText}>건너뛰기</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.center}>
        <View style={[styles.iconBadge, { backgroundColor: step.bg }]}>
          <Ionicons name={step.iconName} size={64} color={step.iconColor} />
        </View>
        <View style={styles.textGroup}>
          <Text weight="bold" style={styles.title}>
            {step.title}
          </Text>
          <Text style={styles.description}>{step.description}</Text>
        </View>
      </View>

      <View style={styles.dotsRow}>
        {STEPS.map((_, index) => (
          <View
            key={index}
            style={[styles.dot, index === stepIndex ? styles.dotActive : styles.dotInactive]}
          />
        ))}
      </View>

      <View style={styles.bottom}>
        <TouchableOpacity style={styles.ctaButton} onPress={handleNext} activeOpacity={0.88}>
          <Text weight="semiBold" style={styles.ctaText}>
            {step.cta}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

function createStyles(colors: ThemeColors) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    skipRow: {
      alignItems: 'flex-end',
      paddingHorizontal: 20,
      paddingTop: 8,
    },
    skipText: {
      fontSize: 15,
      color: colors.textMuted,
    },
    center: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      paddingHorizontal: 36,
      gap: 28,
    },
    iconBadge: {
      width: 148,
      height: 148,
      borderRadius: 36,
      alignItems: 'center',
      justifyContent: 'center',
    },
    textGroup: {
      alignItems: 'center',
      gap: 10,
    },
    title: {
      fontSize: 24,
      textAlign: 'center',
      letterSpacing: -0.4,
    },
    description: {
      fontSize: 15,
      lineHeight: 22,
      textAlign: 'center',
      color: colors.textMuted,
    },
    dotsRow: {
      flexDirection: 'row',
      justifyContent: 'center',
      gap: 7,
      paddingBottom: 22,
    },
    dot: {
      height: 7,
      borderRadius: 4,
    },
    dotActive: {
      width: 20,
      backgroundColor: BRAND_COLOR,
    },
    dotInactive: {
      width: 7,
      backgroundColor: colors.border,
    },
    bottom: {
      paddingHorizontal: 20,
      paddingBottom: 24,
    },
    ctaButton: {
      height: 52,
      borderRadius: 16,
      backgroundColor: BRAND_COLOR,
      alignItems: 'center',
      justifyContent: 'center',
    },
    ctaText: {
      fontSize: 16,
      color: '#fff',
    },
  });
}
