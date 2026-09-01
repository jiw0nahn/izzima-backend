import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

// Shared by contexts/AuthContext.tsx (writes on login/logout) and lib/api.ts
// (reads to attach Authorization headers) so both agree on where the
// session lives without importing each other.
//
// isLoggedIn is just a UI flag (no harm if it leaked), so it stays in
// AsyncStorage. accessToken is a real credential — it goes into
// expo-secure-store (Keychain on iOS / Keystore on Android) instead of
// AsyncStorage, which is a plain unencrypted file on disk.
const IS_LOGGED_IN_KEY = 'izzima:isLoggedIn';
// SecureStore 키는 영문/숫자/'.'/'-'/'_'만 허용해서(AsyncStorage와 달리 ':' 불가) 점으로 구분.
const ACCESS_TOKEN_KEY = 'izzima.accessToken';

export async function getStoredAuth(): Promise<{ isLoggedIn: boolean; accessToken: string | null }> {
  const [isLoggedIn, accessToken] = await Promise.all([
    AsyncStorage.getItem(IS_LOGGED_IN_KEY),
    SecureStore.getItemAsync(ACCESS_TOKEN_KEY),
  ]);
  return { isLoggedIn: isLoggedIn === 'true', accessToken };
}

// accessToken is optional because the 이메일 로그인 button still only
// simulates a successful login (no real Supabase session yet) — for a real
// session, pass the access_token here and lib/api.ts's getAccessToken()
// starts sending it automatically.
export async function setStoredAuth(accessToken?: string): Promise<void> {
  await AsyncStorage.setItem(IS_LOGGED_IN_KEY, 'true');
  if (accessToken) {
    await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
  }
}

export async function clearStoredAuth(): Promise<void> {
  await Promise.all([AsyncStorage.removeItem(IS_LOGGED_IN_KEY), SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY)]);
}

export function getStoredAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
}
