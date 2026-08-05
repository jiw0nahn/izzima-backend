import { API_BASE_URL } from "@/constants/config";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
};

export interface UploadImageResponse {
  id: string;
  user_id: string | null;
  storage_path: string;
  ocr_text: string | null;
  caption: string | null;
  category: string | null;
  search_text: string | null;
  created_at: string;
  signed_url: string | null;
}

export async function uploadImage(uri: string): Promise<UploadImageResponse> {
  const filename = uri.split("/").pop() ?? `upload-${Date.now()}.jpg`;
  const extension = filename.split(".").pop()?.toLowerCase();
  const mimeType =
    extension === "png"
      ? "image/png"
      : extension === "webp"
        ? "image/webp"
        : extension === "heic"
          ? "image/heic"
          : "image/jpeg";

  const formData = new FormData();
  // React Native의 FormData는 웹과 달리 { uri, name, type } 객체를 file 필드로 받음
  formData.append("file", {
    uri,
    name: filename,
    type: mimeType,
  } as unknown as Blob);

  const response = await fetch(`${API_BASE_URL}/images`, {
    method: "POST",
    body: formData,
    // Content-Type을 직접 지정하면 안 됨 — fetch가 multipart boundary를 자동 생성해야 함
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `업로드 실패: ${response.status}`);
  }

  return response.json();
}
