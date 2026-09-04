import { Stack } from 'expo-router';

// onboarding/login/login-email을 루트 Stack의 직속 형제로 두고 그 사이를
// push/replace로 옮겨다니면 iOS 네이티브에서 도착 화면이 터치를 아예 못 받는
// 문제가 있었다. (tabs) 그룹(중첩 네비게이터)으로 이동하는 건 항상 정상
// 동작했던 것에 착안해, 이 세 화면도 자체 중첩 Stack으로 묶었다.
export default function AuthLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="onboarding" />
      <Stack.Screen name="login" />
      <Stack.Screen name="login-email" />
    </Stack>
  );
}
