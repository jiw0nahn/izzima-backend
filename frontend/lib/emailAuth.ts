import { supabase } from "@/lib/supabase";

export class EmailAuthNotConfiguredError extends Error {}

export interface EmailSession {
  accessToken: string;
}

function assertConfigured() {
  if (!supabase) {
    throw new EmailAuthNotConfiguredError(
      "Supabase가 설정되지 않았습니다. EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY를 .env에 설정해주세요.",
    );
  }
}

// 이미 가입된 계정으로 로그인.
export async function signInWithEmail(email: string, password: string): Promise<EmailSession> {
  assertConfigured();
  const { data, error } = await supabase!.auth.signInWithPassword({ email, password });
  if (error) {
    throw error;
  }
  const accessToken = data.session?.access_token;
  if (!accessToken) {
    throw new Error("로그인 응답에서 세션을 받지 못했습니다.");
  }
  return { accessToken };
}

export interface EmailSignUpResult {
  accessToken: string | null;
  // Supabase 프로젝트에서 "Confirm email"이 켜져 있으면 가입 직후엔 세션이
  // 없고, 사용자가 메일함의 인증 링크를 눌러야 로그인 상태가 된다.
  needsEmailConfirmation: boolean;
}

// 새 계정 생성.
export async function signUpWithEmail(email: string, password: string): Promise<EmailSignUpResult> {
  assertConfigured();
  const { data, error } = await supabase!.auth.signUp({ email, password });
  if (error) {
    throw error;
  }
  const accessToken = data.session?.access_token ?? null;
  return { accessToken, needsEmailConfirmation: !accessToken };
}
