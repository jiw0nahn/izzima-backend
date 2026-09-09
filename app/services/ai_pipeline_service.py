"""
app/services/ai_pipeline_service.py

AI Pipeline(OCR -> BLIP -> Qwen -> KURE 임베딩) 호출 서비스 경계.

파이프라인을 "호출"하는 인터페이스만 정의.

호출 방식:
GPU 서버 위에서 파이프라인 전체를 감싸는 FastAPI 서버(`POST /analyze`)를 만들고
Cloudflare Tunnel(`cloudflared`)로 노출해둬서 이제 HTTP로 호출.
Cloudflare Tunnel은 GPU 서버가 아웃바운드로 연결을 열어서 공개 URL을 받는 방식이라
인바운드 방화벽 설정 변경 없이도 외부에서 그 URL로 접속할 수 있다.
단, URL은 `cloudflared` 재시작 시 바뀔 수 있어 매번 하드코딩하지 않고 AI_SERVER_URL 환경변수로 받는다.

POST {AI_SERVER_URL}/analyze의 반환 계약 (ai/src/models.py::Event 기준):
    {
      "ocr_result": {...},      # ai/src/ocr.py::OCRService.extract_text() 원본 결과. 사용 안 함.
      "ocr_text": "...",
      "caption": "...",
      "event": {                # ai/src/models.py::Event.model_dump()
        "type": "expiration | exam | assignment_due | reservation
                 | departure | check_in | performance | meeting
                 | schedule | none",
        "title": "string | null",
        "date": "YYYY-MM-DD | null",
        "time": "HH:MM | null",
        "end_time": "HH:MM | null",
        "location": "string | null",
        "search_text": "...",
        "metadata": {
          ...                             # reservation_number/amount 등은
                                          # events 테이블이 아직 스텁이라 지금은 사용 안 함.
        },
      },
      "embedding": [float, ...] | [],   # KURE-v1, search_text가 비어있으면 []
      "used_model": "...",              # 디버깅용, 사용 안 함
      "fallback_used": bool,            # 디버깅용, 사용 안 함
      "fallback_reasons": [...],        # 디버깅용, 사용 안 함
    }

metadata.category 필드는 완전히 삭제됨. event.type과 의미가 중복돼서
실제로는 항상 비거나 부정확하게 채워지고 있었음.
images.type 컬럼은 이제 metadata.category가 아니라 event.type에서 직접 가져옴.
event.type이 "none"이면 images.type도 None으로 남긴다.

event는 events 테이블 대상 데이터다 - events_crud가 아직 스텁이라 지금은 저장하지
않고 호출부에 그대로 전달만 한다. events_crud가 구현되면 라우터에서 event.type이
"none"이 아닐 때만 레코드를 만들면 된다.

검색어(GET /search?q=) 임베딩은 이 서비스가 담당하지 않는다 - /analyze는 이미지
전용이라 텍스트만 임베딩하는 용도로 못 쓴다. app/services/embedding_service.py가
별도로 담당한다 (지금은 여전히 ai/src를 직접 import하는 방식 - AI 서버에 텍스트
임베딩 엔드포인트가 생기면 그쪽도 HTTP로 통일할 수 있음).
"""

import os
from typing import Optional, TypedDict

import httpx
from dotenv import load_dotenv

load_dotenv()

AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "").rstrip("/")

# Qwen 9B->27B 폴백까지 걸릴 수 있어 넉넉하게 잡음. GPU가 다른 작업으로 바쁘면
# 더 오래 걸릴 수 있다 (실제로 직접 확인한 적 있음).
_REQUEST_TIMEOUT_SECONDS = 120.0


class EventInfo(TypedDict):
    type: str
    date: Optional[str]
    time: Optional[str]
    end_time: Optional[str]
    title: Optional[str]
    location: Optional[str]


class AIPipelineResult(TypedDict):
    ocr_text: Optional[str]
    caption: Optional[str]
    search_text: Optional[str]
    embedding: Optional[list[float]]
    event: EventInfo


_EMPTY_EVENT: EventInfo = {
    "type": "none",
    "date": None,
    "time": None,
    "end_time": None,
    "title": None,
    "location": None,
}

_EMPTY_RESULT: AIPipelineResult = {
    "ocr_text": None,
    "caption": None,
    "search_text": None,
    "embedding": None,
    "event": _EMPTY_EVENT,
}


def run_ai_pipeline(file_bytes: bytes, filename: str) -> AIPipelineResult:
    """
    업로드된 이미지 원본으로 OCR 텍스트/캡션/search_text/이벤트(type 포함)/임베딩을
    추출한다. AI 서버(POST {AI_SERVER_URL}/analyze)를 호출한다.

    AI_SERVER_URL이 설정 안 되어 있거나(예: 아직 값을 못 받은 환경), 그 URL에
    접속이 안 되거나(터널이 꺼져있음 등), 호출 자체가 실패하면 빈 결과로
    대체한다. 파이프라인 실패가 업로드 자체를 막아서는 안 되므로 이 함수는
    예외를 던지지 않는다 - 실패 원인은 로깅만 하고 null로 채운 결과를 반환한다.
    """
    if not AI_SERVER_URL:
        return _EMPTY_RESULT

    try:
        response = httpx.post(
            f"{AI_SERVER_URL}/analyze",
            files={"file": (filename, file_bytes)},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        raw = response.json()
    except Exception as error:
        print(f"[ai_pipeline_service] AI 서버 호출 실패: {error}")
        return _EMPTY_RESULT

    event = raw.get("event") or {}

    return {
        "ocr_text": raw.get("ocr_text"),
        "caption": raw.get("caption"),
        "search_text": event.get("search_text"),
        "embedding": raw.get("embedding") or None,
        "event": {
            "type": event.get("type", "none"),
            "date": event.get("date"),
            "time": event.get("time"),
            "end_time": event.get("end_time"),
            "title": event.get("title"),
            "location": event.get("location"),
        },
    }
