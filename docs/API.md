# 이미지 API 명세 (v0.1.0)

프론트엔드(React Native) 연동용 문서. 이 문서에 없는 최신 스키마/에러 케이스는
서버 실행 후 `http://<host>:8000/docs` (Swagger UI) 또는 `/openapi.json`에서
항상 최신 상태로 확인 가능합니다.

- Base URL: 로컬 개발 시 `http://127.0.0.1:8000` (배포 URL은 별도 공지)
- 인증: **없음.** 현재 모든 엔드포인트는 누구나 호출 가능하고, 소유권 필터링이
  없습니다 (`GET /images`가 전체 사용자의 이미지를 반환). auth 도입 전까지는
  프론트에서 사용자별 데이터 분리를 기대하면 안 됩니다.
- 데이터 형식: 요청은 `multipart/form-data`(업로드) 또는 없음, 응답은 전부 JSON.

## 공통 사항

### 이미지 객체 (`ImageResponse`)

`POST /images`, `GET /images/{id}`, `GET /images`의 각 항목이 공통으로 이 형태입니다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (uuid) | 이미지 레코드 id |
| `user_id` | string \| null | 업로더 id. **auth 미도입 상태라 현재 항상 null.** |
| `storage_path` | string | Storage 상의 object key (프론트에서 직접 쓸 일 없음, 참고용) |
| `ocr_text` | string \| null | OCR 텍스트. **AI Pipeline 미연동이라 현재 항상 null.** |
| `caption` | string \| null | 이미지 캡션. **현재 항상 null.** |
| `category` | string \| null | 분류 카테고리. **현재 항상 null** — 폴더 UI는 이 필드가 채워지기 전까지 보류. |
| `search_text` | string \| null | 자연어 검색용 텍스트. **현재 항상 null.** |
| `created_at` | string (ISO 8601 datetime) | 생성 시각 |
| `signed_url` | string \| null | private 버킷의 임시 서명 URL. **기본 24시간 후 만료 — 캐시/영구 저장하지 말고, 화면에 진입할 때마다 새로 받은 응답의 값을 사용할 것.** 서명 발급 자체가 실패한 경우 null일 수 있음. |

### 에러 응답

FastAPI 기본 형식을 그대로 사용합니다.

```json
{ "detail": "사람이 읽을 수 있는 에러 메시지" }
```

| 상태 코드 | 의미 |
|---|---|
| 400 | 잘못된 요청 (지원하지 않는 확장자, 용량 초과 등) |
| 404 | 대상 리소스 없음 |
| 502 | 서버가 Supabase(Storage/DB) 호출에 실패 |

---

## `POST /images` — 이미지 업로드

이미지를 Storage(private 버킷)에 업로드하고 `images` 테이블에 레코드를 생성합니다.

- Request: `multipart/form-data`
  - `file`: 이미지 파일 (필수)
  - 허용 확장자: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`
  - 최대 용량: 15MB
- Response: `201 Created`, body는 `ImageResponse`

```json
{
  "id": "5097ae32-7ce8-483a-81b3-a643123c115b",
  "user_id": null,
  "storage_path": "2026/07/28/495edd2fedd547e9b7c38b1f6b6e17e3.png",
  "ocr_text": null,
  "caption": null,
  "category": null,
  "search_text": null,
  "created_at": "2026-07-28T10:36:40.151052Z",
  "signed_url": "https://xxxx.supabase.co/storage/v1/object/sign/images/...&token=..."
}
```

에러:
- `400` — 지원하지 않는 확장자 / 용량 초과
- `502` — 업로드 또는 DB 레코드 생성 실패 (DB 실패 시 방금 올린 Storage 파일은 서버가 자동 롤백/삭제함)

주의: `ocr_text`/`caption`/`category`/`search_text`는 AI Pipeline이 아직 연동되지
않아 **항상 null**로 내려옵니다. 프론트에서 이 필드들에 의존하는 화면(자동 분류
폴더, 캡션 표시 등)은 지금 단계에서 목데이터로 개발하고, 실제 값은 파이프라인
연동 후 별도 공지 예정입니다.

---

## `GET /images/{image_id}` — 이미지 상세 조회

- Path param: `image_id` (uuid string)
- Response: `200 OK`, body는 `ImageResponse`
- `404` — 해당 id의 이미지가 없음

주의: 소유권 검증이 없어 `image_id`만 알면 누구나 조회 가능합니다 (auth 도입 전 임시 상태).

---

## `GET /images` — 이미지 목록 조회 (최신순, 평면 목록)

- Query params:
  - `limit` (int, 1~100, 기본 20)
  - `offset` (int, 0 이상, 기본 0)
- Response: `200 OK`

```json
{
  "data": [ /* ImageResponse[], created_at 내림차순 */ ]
}
```

주의:
- 카테고리 폴더링 없음 — 모든 `category`가 null이라 지금은 폴더 UI에 쓸 수 없는 단순 리스트입니다.
- 소유권 필터링 없음 — 전체 사용자의 이미지가 한 목록에 섞여 반환됩니다.
- offset 기반 페이지네이션 — 총 개수(`total`)는 응답에 없으므로, "다음 페이지 있음" 여부는
  `data.length == limit`인지로 판단하세요 (같으면 다음 페이지가 있을 수 있음).

---

## 아직 없는 것 (프론트에서 기대하면 안 되는 기능)

- 로그인/인증, 사용자별 데이터 분리
- 카테고리 폴더 UI에 쓸 수 있는 실제 `category` 값
- 자연어 검색 API (`search_text`/pgvector 기반) — `embeddings_crud`/`embedding_service`가 아직 스텁
- 만료 이벤트(D-day) 추천 카드 API — `events_crud`가 아직 스텁
- 이미지 삭제 API
