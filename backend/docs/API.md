# 이미지/이벤트 API 명세 (v0.1.0)

프론트엔드(React Native) 연동용 문서. 이 문서에 없는 최신 스키마/에러 케이스는
서버 실행 후 `http://<host>:8000/docs` (Swagger UI) 또는 `/openapi.json`에서
항상 최신 상태로 확인 가능합니다.

- Base URL: izzima-production.up.railway.app
- 인증: **필수.** 모든 엔드포인트가 `Authorization: Bearer <supabase-access-token>`
  헤더를 요구합니다 (Supabase Auth JWT). 헤더가 없거나 토큰이 유효하지 않으면
  `401`. 모든 조회/수정/삭제는 토큰에서 추출한 사용자 소유 레코드로만 제한되고,
  다른 사용자의 리소스는 (403이 아니라) `404`로 응답해 존재 여부 자체를
  노출하지 않습니다.
- 데이터 형식: 요청은 `multipart/form-data`(업로드) 또는 없음, 응답은 전부 JSON.

## 공통 사항

### 이미지 객체 (`ImageResponse`)

`POST /images`, `GET /images/{id}`, `GET /images`의 각 항목이 공통으로 이 형태입니다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (uuid) | 이미지 레코드 id |
| `user_id` | string \| null | 업로더 uuid (인증 토큰의 sub claim) |
| `storage_path` | string | Storage 상의 object key (프론트에서 직접 쓸 일 없음, 참고용) |
| `ocr_text` | string \| null | OCR 텍스트. **AI Pipeline 미연동이라 현재 항상 null.** |
| `caption` | string \| null | 이미지 캡션. **현재 항상 null.** |
| `category` | string \| null | 분류 카테고리. **현재 항상 null** — 폴더 UI는 이 필드가 채워지기 전까지 보류. |
| `search_text` | string \| null | 자연어 검색용 텍스트. **현재 항상 null.** |
| `created_at` | string (ISO 8601 datetime) | 생성 시각 |
| `signed_url` | string \| null | private 버킷의 임시 서명 URL. **기본 24시간 후 만료 — 캐시/영구 저장하지 말고, 화면에 진입할 때마다 새로 받은 응답의 값을 사용할 것.** 서명 발급 자체가 실패한 경우 null일 수 있음. |

### 이벤트 객체 (`EventResponse`)

`GET /images/{image_id}/events`, `GET /events`의 각 항목이 공통으로 이 형태입니다.
AI Pipeline이 이미지 업로드 시 이벤트 정보를 추출한 경우에만 생성되고, 지금은
GPU 서버 쪽 Qwen 연동이 막혀 있어 **실제로는 항상 빈 목록**이 내려갑니다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (uuid) | 이벤트 레코드 id |
| `image_id` | string (uuid) | 이 이벤트가 추출된 원본 이미지 id |
| `event_type` | string | `expiration`/`exam`/`assignment_due`/`reservation`/`departure`/`check_in`/`performance`/`meeting`/`schedule` 중 하나 (`none`은 저장되지 않음) |
| `title` | string \| null | |
| `event_date` | string \| null | `YYYY-MM-DD` |
| `event_time` | string \| null | `HH:MM` |
| `location` | string \| null | |
| `created_at` | string (ISO 8601 datetime) | 생성 시각 |

### 에러 응답

FastAPI 기본 형식을 그대로 사용합니다.

```json
{ "detail": "사람이 읽을 수 있는 에러 메시지" }
```

| 상태 코드 | 의미 |
|---|---|
| 400 | 잘못된 요청 (지원하지 않는 확장자, 용량 초과 등) |
| 404 | 대상 리소스 없음 |
| 422 | 요청 body 유효성 검증 실패 (예: `category`가 허용된 8개 값 밖) |
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
  "user_id": "b6e0a9f2-1234-4a5b-9c3d-abcdef123456",
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
- `404` — 해당 id의 이미지가 없음, 또는 요청자 소유가 아님

---

## `PATCH /images/{image_id}/category` — 이미지 카테고리 변경

AI Pipeline(Qwen)이 잘못 분류했을 때 사용자가 직접 보정하는 용도입니다.

- Path param: `image_id` (uuid string)
- Request body (JSON):

```json
{ "category": "coupon" }
```

  - `category`: 다음 8개 값 중 하나만 허용 — `coupon`, `ticket`, `reservation`,
    `academic`, `receipt`, `document`, `photo`, `other`. 그 외 값은 `422`.
- Response: `200 OK`, body는 `ImageResponse` (변경된 `category` 반영)
- `404` — 해당 id의 이미지가 없음, 또는 요청자 소유가 아님
- `422` — `category`가 허용 목록 밖의 값

---

## `DELETE /images/{image_id}` — 이미지 삭제

이미지 레코드(DB)와 Storage 파일을 함께 삭제합니다.

- Path param: `image_id` (uuid string)
- Response: `204 No Content` (body 없음)
- `404` — 해당 id의 이미지가 없음, 또는 요청자 소유가 아님
- `502` — DB 레코드 삭제 실패 (이 경우 Storage 파일 삭제는 시도하지 않음)

주의:
- 딸린 이벤트(`events`)가 먼저 정리되고 나서 이미지 레코드가 삭제됩니다.
- 삭제는 되돌릴 수 없습니다 (soft delete 아님).
- DB 레코드 삭제 후 Storage 파일 삭제를 시도하지만, Storage 삭제 실패는 조용히
  무시되므로(이미 없는 파일일 수 있음) 드물게 Storage에 고아 파일이 남을 수 있습니다.

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
- 요청자 소유 이미지만 반환합니다.
- offset 기반 페이지네이션 — 총 개수(`total`)는 응답에 없으므로, "다음 페이지 있음" 여부는
  `data.length == limit`인지로 판단하세요 (같으면 다음 페이지가 있을 수 있음).

---

## `GET /images/{image_id}/events` — 특정 이미지에 딸린 이벤트 조회

- Path param: `image_id` (uuid string)
- Response: `200 OK`

```json
{
  "data": [ /* EventResponse[] — 보통 0개 또는 1개 */ ]
}
```

- `404` — 해당 id의 이미지가 없음, 또는 요청자 소유가 아님

주의: AI Pipeline의 Qwen 연동이 아직 막혀 있어 지금은 항상 `data: []`가 내려옵니다.

---

## `GET /events` — 요청자 전체 이벤트 목록 (D-day 추천 카드용)

- Query params:
  - `upcoming` (bool, 기본값 `false`) — `true`면 지난 이벤트와 `event_date`가 없는 이벤트를 제외하고 앞으로 다가올 이벤트만 반환 (D-day 카드 후보만 걸러줌). `false`(기본값)는 기존과 동일하게 전부 반환.
- Response: `200 OK`

```json
{
  "data": [ /* EventResponse[], event_date 오름차순(가까운 D-day가 먼저). upcoming=false일 때는 날짜 없는 이벤트도 뒤로 밀려 포함됨 */ ]
}
```

주의:
- 페이지네이션 없음 — 사용자당 이벤트 수가 적다고 보고 전체를 한 번에 반환합니다. 늘어나면 바뀔 수 있습니다.
- D-day 숫자 계산(오늘부터 며칠 남았는지)은 이 API의 책임이 아닙니다 — `event_date`만 내려주고 프론트가 계산합니다. 추천 카드 노출 개수 제한도 프론트 책임입니다. `upcoming=true`는 "카드 후보가 될 수 있는지"만 걸러줍니다.
- AI Pipeline의 Qwen 연동이 아직 막혀 있어 지금은 항상 `data: []`가 내려옵니다.

---

## 아직 없는 것 (프론트에서 기대하면 안 되는 기능)

- 카테고리 폴더 UI에 쓸 수 있는 실제 `category` 값
- 자연어 검색 API (`search_text`/pgvector 기반) — `embeddings_crud`는 구현됐지만 `embedding_service`(KURE-v1 호출)가 아직 스텁
- 실제 이벤트 데이터 — `events_crud`/`/events` API 자체는 구현됐지만, GPU 서버의 Qwen(Ollama)이 응답하지 않아 이벤트가 생성되지 않음
- 이미지 태그(`image_tags`) 관련 API — 테이블 자체가 아직 crud/router 없음
