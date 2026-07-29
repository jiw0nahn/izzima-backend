"""
app/services/ai_pipeline_service.py

AI Pipeline(OCR -> BLIP -> Qwen2.5-Instruct -> KURE-v1) 호출 서비스 경계.

모델 내부(OCR/캡셔닝/구조화 추출/임베딩 튜닝)는 팀원 담당이므로 이 파일은
그 파이프라인을 "호출"하는 인터페이스만 정의한다.

호출 방식: HTTP가 아니라 monorepo의 형제 패키지 `ai/`를 직접 import해서 함수
호출한다 (ai/pipeline.py::run_pipeline(image_bytes) -> dict). ai 쪽 함수들은
현재 전부 NotImplementedError를 던지는 스텁이라, 이 서비스도 결과적으로는
빈 값을 반환하는 상태다 — 다만 진짜 파이프라인이 채워지면 이 파일은 손댈 필요
없이 그대로 동작한다.

ai.pipeline.run_pipeline()의 반환 계약:
    {
      "ocr_text": "...",
      "caption": "...",
      "structured": {           # ai/structuring.py::extract_structured_info() 결과.
                                 # Qwen 구조화 추출 스펙(최종 확정본)을 따를 것으로 가정:
        "primary_category": "coupon | ticket | reservation | academic
                              | receipt | document | photo | other",
        "search_text": "...",
        "event": {
          "type": "expiration | exam | assignment_due | reservation
                   | departure | check_in | performance | meeting
                   | schedule | none",
          "date": "YYYY-MM-DD | null",
          "time": "HH:MM | null",
          "title": "string | null",
          "location": "string | null",
        },
      },
      "embedding": [...],       # KURE-v1 벡터 - image_embeddings 대상,
                                 # embedding_service.py 책임 범위라 이 서비스에서는 사용하지 않는다.
    }

event는 events 테이블 대상 데이터다 — events_crud가 아직 스텁이라 지금은 저장하지
않고 호출부에 그대로 전달만 한다. events_crud가 구현되면 라우터에서 event.type이
"none"이 아닐 때만 레코드를 만들면 된다.
"""

import sys
from pathlib import Path
from typing import Optional, TypedDict

# ai/ 패키지는 이 파일 기준 backend/의 부모 디렉터리(모노레포 루트)에 형제로 있다.
# backend/app/services/ai_pipeline_service.py -> parents[3] == 모노레포 루트
_MONOREPO_ROOT = Path(__file__).resolve().parents[3]
if str(_MONOREPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_MONOREPO_ROOT))

try:
    from ai.pipeline import run_pipeline as _run_pipeline
except ImportError:
    _run_pipeline = None


class EventInfo(TypedDict):
    type: str
    date: Optional[str]
    time: Optional[str]
    title: Optional[str]
    location: Optional[str]


class AIPipelineResult(TypedDict):
    ocr_text: Optional[str]
    caption: Optional[str]
    primary_category: Optional[str]
    search_text: Optional[str]
    event: EventInfo


_EMPTY_EVENT: EventInfo = {
    "type": "none",
    "date": None,
    "time": None,
    "title": None,
    "location": None,
}

_EMPTY_RESULT: AIPipelineResult = {
    "ocr_text": None,
    "caption": None,
    "primary_category": None,
    "search_text": None,
    "event": _EMPTY_EVENT,
}


def run_ai_pipeline(file_bytes: bytes, filename: str) -> AIPipelineResult:
    """
    업로드된 이미지 원본으로 OCR 텍스트/캡션/카테고리/search_text/이벤트 정보를 추출한다.

    ai.pipeline.run_pipeline()이 아직 NotImplementedError를 던지는 스텁이거나,
    ai/ 패키지 자체를 import할 수 없는 환경(예: ai/ 없이 backend/만 배포된 경우)
    이면 빈 결과로 대체한다. 파이프라인 실패가 업로드 자체를 막아서는 안 되므로
    이 함수는 예외를 던지지 않는다 — 실패 원인은 로깅만 하고 null로 채운 결과를
    반환한다.
    """
    if _run_pipeline is None:
        return _EMPTY_RESULT

    try:
        raw = _run_pipeline(file_bytes)
    except Exception as error:
        print(f"[ai_pipeline_service] run_pipeline 실패: {error}")
        return _EMPTY_RESULT

    structured = raw.get("structured") or {}

    return {
        "ocr_text": raw.get("ocr_text"),
        "caption": raw.get("caption"),
        "primary_category": structured.get("primary_category"),
        "search_text": structured.get("search_text"),
        "event": structured.get("event") or _EMPTY_EVENT,
    }
