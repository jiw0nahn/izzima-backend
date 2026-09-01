import * as Linking from "expo-linking";
import * as WebBrowser from "expo-web-browser";

import { supabase } from "@/lib/supabase";

export class KakaoLoginNotConfiguredError extends Error {}

export interface KakaoSession {
  accessToken: string;
}

export async function signInWithKakao(): Promise<KakaoSession> {
  if (!supabase) {
    throw new KakaoLoginNotConfiguredError(
      "Supabase가 설정되지 않았습니다. EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY를 .env에 설정해주세요.",
    );
  }

  const redirectTo = Linking.createURL("/", { scheme: "izzima" });

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "kakao",
    options: { redirectTo, skipBrowserRedirect: true },
  });
  if (error || !data?.url) {
    throw error ?? new Error("카카오 로그인 URL을 받아오지 못했습니다.");
  }

  // preferEphemeralSession: 기기의 일반 Safari 쿠키/로그인 세션과 분리된
  // 상태로 카카오 인증 화면을 띄운다. 이게 없으면 사용자가 Safari에 로그인해둔
  // 다른 세션과 공유되거나, 재설치 후에도 이전 카카오 로그인이 남아있을 수 있음.
  const result = await WebBrowser.openAuthSessionAsync(data.url, redirectTo, {
    preferEphemeralSession: true,
  });
  if (result.type !== "success" || !result.url) {
    throw new Error("카카오 로그인이 취소되었습니다.");
  }

  // Supabase는 access_token을 쿼리가 아니라 URL fragment(#...)로 돌려준다.
  const fragment = result.url.split("#")[1] ?? "";
  const params = new URLSearchParams(fragment);
  const accessToken = params.get("access_token");
  if (!accessToken) {
    throw new Error("로그인 응답에서 access_token을 찾지 못했습니다.");
  }

  return { accessToken };
}
