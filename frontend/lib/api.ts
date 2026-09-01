import { API_BASE_URL } from "@/constants/config";
import { getStoredAccessToken } from "@/lib/authStorage";

async function getAccessToken(): Promise<string | null> {
  return getStoredAccessToken();
}

async function authHeaders(
  extra?: Record<string, string>,
): Promise<Record<string, string>> {
  const token = await getAccessToken();
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: await authHeaders({
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string> | undefined),
    }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(
      body?.detail ??
        `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  if (response.status === 204) {
    return undefined as T;
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
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: (path: string) => request<void>(path, { method: "DELETE" }),
};

export type ImageCategory =
  | "coupon"
  | "ticket"
  | "reservation"
  | "academic"
  | "receipt"
  | "document"
  | "photo"
  | "other";

export interface ImageResponse {
  id: string;
  user_id: string | null;
  storage_path: string;
  ocr_text: string | null;
  caption: string | null;
  category: ImageCategory | null;
  search_text: string | null;
  created_at: string;
  signed_url: string | null;
}

export interface ImageListResponse {
  data: ImageResponse[];
}

export async function uploadImage(uri: string): Promise<ImageResponse> {
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
  formData.append("file", {
    uri,
    name: filename,
    type: mimeType,
  } as unknown as Blob);

  const response = await fetch(`${API_BASE_URL}/images`, {
    method: "POST",
    body: formData,
    headers: await authHeaders(),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `업로드 실패: ${response.status}`);
  }

  return response.json();
}

export function getImage(imageId: string): Promise<ImageResponse> {
  return api.get<ImageResponse>(`/images/${imageId}`);
}

export function listImages(params?: {
  limit?: number;
  offset?: number;
}): Promise<ImageListResponse> {
  const query = new URLSearchParams();
  if (params?.limit != null) query.set("limit", String(params.limit));
  if (params?.offset != null) query.set("offset", String(params.offset));
  const qs = query.toString();
  return api.get<ImageListResponse>(`/images${qs ? `?${qs}` : ""}`);
}

export function updateImageCategory(
  imageId: string,
  category: ImageCategory,
): Promise<ImageResponse> {
  return api.patch<ImageResponse>(`/images/${imageId}/category`, { category });
}

export function deleteImage(imageId: string): Promise<void> {
  return api.delete(`/images/${imageId}`);
}
