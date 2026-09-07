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
| `ocr_text` | string \| null | OCR 텍스트. AI 서버(`AI_SERVER_URL`) 호출이 안 되는 환경/실패 시 null. |
| `caption` | string \| null | 이미지 캡션. 위와 동일한 조건에서만 채워짐. |
| `category` | string \| null | 분류 카테고리(자유 텍스트, 8개 고정값 아님). 이벤트가 없는 이미지(영수증/사진/문서 등)는 null일 수 있음 — 폴더 UI는 이 필드가 안정적으로 채워지기 전까지 보류. |
| `search_text` | string \| null | 자연어 검색용 텍스트. |
| `created_at` | string (ISO 8601 datetime) | 생성 시각 |
| `signed_url` | string \| null | private 버킷의 임시 서명 URL. **기본 24시간 후 만료 — 캐시/영구 저장하지 말고, 화면에 진입할 때마다 새로 받은 응답의 값을 사용할 것.** 서명 발급 자체가 실패한 경우 null일 수 있음. |

### 이벤트 객체 (`EventResponse`)

`GET /images/{image_id}/events`, `GET /events`의 각 항목이 공통으로 이 형태입니다.
AI Pipeline이 이미지 업로드 시 이벤트 정보를 추출한 경우에만 생성되고, 이벤트가
없는 이미지(영수증/사진/문서 등)는 애초에 이 레코드 자체가 없습니다. AI 서버
(`AI_SERVER_URL`)를 호출할 수 없는 환경/실패 시에는 이벤트 자체가 생성되지
않습니다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (uuid) | 이벤트 레코드 id |
| `image_id` | string (uuid) | 이 이벤트가 추출된 원본 이미지 id |
| `event_type` | string | `expiration`/`exam`/`assignment_due`/`reservation`/`departure`/`check_in`/`performance`/`meeting`/`schedule` 중 하나 (`none`은 저장되지 않음) |
| `title` | string \| null | |
| `event_date` | string \| null | `YYYY-MM-DD` |
| `event_time` | string \| null | `HH:MM` |
| `location` | string \| null | |
| `is_used` | boolean | 사용자가 상세 화면에서 "사용 완료"로 표시했는지 여부. 기본 `false`, `PATCH /events/{event_id}/used`로 수정. 만료 여부는 별도 필드 없이 `event_date`로 프론트에서 계산할 것. |
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
같은 요청 안에서 AI Pipeline(OCR/캡션/카테고리/search_text/이벤트/임베딩)을
동기로 호출해 결과까지 함께 저장합니다 (AI 서버가 GPU 서버 위에서 Cloudflare
Tunnel로 노출돼 있어, 백엔드가 Railway든 어디든 HTTP로 호출 가능).

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
  "ocr_text": "MEGABOX TICKET\n부산대 7관(9층)\n...",
  "caption": "a screenshot of a movie ticket",
  "category": null,
  "search_text": "예약 예매 2026-06-19 20:45 부산대 7관(9층)",
  "created_at": "2026-07-28T10:36:40.151052Z",
  "signed_url": "https://xxxx.supabase.co/storage/v1/object/sign/images/...&token=..."
}
```

에러:
- `400` — 지원하지 않는 확장자 / 용량 초과
- `502` — 업로드 또는 DB 레코드 생성 실패 (DB 실패 시 방금 올린 Storage 파일은 서버가 자동 롤백/삭제함)

주의: `ocr_text`/`caption`/`category`/`search_text`는 AI 서버(`AI_SERVER_URL`)
호출이 안 되는 환경이거나 그 호출이 실패하면 **null**로 내려옵니다 (업로드
자체는 실패하지 않음 — AI 실패가 업로드를 막지 않도록 설계됨). `category`는
이벤트가 없는 이미지에서는 null일 수 있습니다. AI 서버가 응답하기까지 시간이
좀 걸릴 수 있어(GPU 부하에 따라 다름) 이 요청 자체의 응답도 그만큼 늦어질 수
있습니다.

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

주의: 이벤트가 없는 이미지(영수증/사진/문서 등)는 항상 `data: []`입니다. AI
서버 호출이 안 되는 환경/실패 시에도 이벤트가 생성되지 않아 `data: []`입니다.

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
- 이벤트가 생성된 이미지가 없으면(AI 서버 호출 불가/실패 포함) 항상 `data: []`입니다.

---

## `PATCH /events/{event_id}/used` — 이벤트 사용 완료 여부 수정

쿠폰/티켓/예약처럼 마감일이 있는 이벤트를 사용자가 상세 화면에서 "사용 완료"로
표시(또는 해제)합니다. 이벤트가 없는 이미지(영수증/사진/문서 등)는 이벤트
레코드 자체가 없어 이 API의 대상이 아닙니다.

- Path param: `event_id` (uuid string)
- Request body:

```json
{ "is_used": true }
```

- Response: `200 OK`, body는 `EventResponse` (수정된 이벤트 전체)

에러:
- `404` — 해당 id의 이벤트가 없음, 또는 그 이벤트가 딸린 이미지가 요청자 소유가 아님
- `422` — `is_used`가 boolean이 아님

주의: 대상 이미지에 이벤트 자체가 생성 안 됐으면(이벤트 없는 이미지, 또는 AI
서버 호출 불가/실패) 수정할 이벤트가 없어 404가 내려옵니다.

---

## `GET /search` — 자연어 이미지 검색

검색어를 KURE-v1으로 임베딩해, 업로드 시 저장해둔 `image_embeddings`와 pgvector
코사인 유사도로 비교한 뒤 가까운 순으로 이미지를 반환합니다.

- Query params:
  - `q` (string, 필수) — 검색어(자연어)
  - `limit` (int, 1~100, 기본 20)
- Response: `200 OK`

```json
{
  "data": [ /* (ImageResponse 필드 전체) + similarity(float, 1에 가까울수록 유사) */ ]
}
```

에러:
- `503` — AI 서버(`AI_SERVER_URL`)를 호출할 수 없어(설정 안 됨/터널 꺼짐/실패) 검색어
  임베딩 자체를 만들 수 없음. 빈 결과(`data: []`)와 구분하기 위해 일부러 에러로
  응답합니다.
- `502` — Supabase 쪽 유사도 검색(rpc) 호출 실패

검색어는 AI 서버의 `POST {AI_SERVER_URL}/embed-query`를 호출해 KURE-v1
임베딩으로 변환합니다 (직접 `ai/src` import 아님, HTTP 호출이라 Railway 배포
환경에서도 동작). `AI_SERVER_URL`이 최신 값으로 설정돼 있어야 합니다.

---

## 아직 없는 것 (프론트에서 기대하면 안 되는 기능)

- 카테고리 폴더 UI에 쓸 수 있는 실제 `category` 값
- 안정적인 자연어 검색/이벤트 데이터 — `POST /images`/`GET /search` 둘 다 AI 서버(`AI_SERVER_URL`)를 HTTP로 호출해 실제 동작하지만, 그 서버가 GPU 서버에서 Cloudflare Tunnel로 임시 노출된 상태라 터널 URL이 바뀌거나 꺼지면 둘 다 다시 안 됨 (503/이벤트 미생성)
- 이미지 태그(`image_tags`) 관련 API — 테이블 자체가 아직 crud/router 없음
