import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { ActivityIndicator, Alert, Pressable, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Text } from '@/components/Text';
import { TextInput } from '@/components/TextInput';
import type { ThemeColors } from '@/constants/colors';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { signInWithEmail, signUpWithEmail } from '@/lib/emailAuth';

const BRAND_COLOR = '#2F6FED';
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 6;

type Mode = 'signin' | 'signup';

export default function EmailLoginScreen() {
  const { colors } = useTheme();
  const { login } = useAuth();
  const styles = useMemo(() => createStyles(colors), [colors]);
  const [mode, setMode] = useState<Mode>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isSignUp = mode === 'signup';

  const handleSubmit = async () => {
    if (!EMAIL_PATTERN.test(email)) {
      Alert.alert('이메일을 확인해주세요', '올바른 이메일 형식이 아니에요.');
      return;
    }
    if (isSignUp && password.length < MIN_PASSWORD_LENGTH) {
      Alert.alert('비밀번호를 확인해주세요', `비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 해요.`);
      return;
    }
    if (!isSignUp && password.length === 0) {
      Alert.alert('비밀번호를 입력해주세요');
      return;
    }

    setIsSubmitting(true);
    try {
      if (isSignUp) {
        const result = await signUpWithEmail(email, password);
        if (result.needsEmailConfirmation || !result.accessToken) {
          Alert.alert(
            '이메일을 확인해주세요',
            '가입을 완료하려면 받은 이메일의 인증 링크를 눌러주세요. 인증 후 로그인해주세요.',
          );
          setMode('signin');
          return;
        }
        await login(result.accessToken);
      } else {
        const { accessToken } = await signInWithEmail(email, password);
        await login(accessToken);
      }
    } catch (err) {
      Alert.alert(
        isSignUp ? '회원가입 실패' : '로그인 실패',
        err instanceof Error ? err.message : '알 수 없는 오류가 발생했어요.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={8}>
          <Ionicons name="chevron-back" size={24} color={colors.text} />
        </Pressable>
      </View>

      <View style={styles.content}>
        <Text weight="bold" style={styles.title}>
          {isSignUp ? '이메일로 회원가입' : '이메일로 로그인'}
        </Text>

        <View style={styles.form}>
          <View style={styles.field}>
            <Text weight="semiBold" style={styles.label}>
              이메일
            </Text>
            <TextInput
              style={[styles.input, { borderColor: colors.border }]}
              placeholder="example@izzima.com"
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
            />
          </View>

          <View style={styles.field}>
            <Text weight="semiBold" style={styles.label}>
              비밀번호
            </Text>
            <TextInput
              style={[styles.input, { borderColor: colors.border }]}
              placeholder={isSignUp ? `${MIN_PASSWORD_LENGTH}자 이상 입력하세요` : '비밀번호를 입력하세요'}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>
        </View>

        <TouchableOpacity
          style={styles.submitButton}
          onPress={handleSubmit}
          disabled={isSubmitting}
          activeOpacity={0.88}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text weight="semiBold" style={styles.submitButtonText}>
              {isSignUp ? '회원가입' : '로그인'}
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setMode(isSignUp ? 'signin' : 'signup')}
          activeOpacity={0.6}
          style={styles.toggleModeButton}
        >
          <Text style={styles.toggleModeText}>
            {isSignUp ? '이미 계정이 있으신가요? ' : '계정이 없으신가요? '}
            <Text weight="semiBold" style={styles.toggleModeLink}>
              {isSignUp ? '로그인' : '회원가입'}
            </Text>
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
    header: {
      paddingHorizontal: 20,
      paddingTop: 8,
    },
    content: {
      flex: 1,
      paddingHorizontal: 28,
      paddingTop: 24,
    },
    title: {
      fontSize: 22,
      letterSpacing: -0.3,
      marginBottom: 28,
    },
    form: {
      gap: 20,
    },
    field: {
      gap: 8,
    },
    label: {
      fontSize: 13,
      color: colors.textMuted,
    },
    input: {
      height: 52,
      borderRadius: 14,
      borderWidth: 1,
      paddingHorizontal: 16,
      fontSize: 16,
    },
    submitButton: {
      height: 52,
      borderRadius: 16,
      backgroundColor: BRAND_COLOR,
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: 32,
    },
    submitButtonText: {
      fontSize: 16,
      color: '#fff',
    },
    toggleModeButton: {
      marginTop: 16,
      alignItems: 'center',
    },
    toggleModeText: {
      fontSize: 14,
      color: colors.textMuted,
    },
    toggleModeLink: {
      fontSize: 14,
      color: BRAND_COLOR,
    },
  });
}
