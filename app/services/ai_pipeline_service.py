"""
app/services/ai_pipeline_service.py

AI Pipeline(OCR -> BLIP -> Qwen2.5-Instruct) 호출 서비스 경계.

모델 내부(OCR/캡셔닝/구조화 추출)는 팀원(문진서) 담당이므로 이 파일은 그
파이프라인을 "호출"하는 인터페이스만 정의한다.

호출 방식: HTTP가 아니라 monorepo의 형제 패키지 `ai/src/`를 직접 import해서
함수 호출한다 (ai/src/pipeline.py::run_pipeline(image_bytes) -> dict).
`ai/src/pipeline.py`가 내부에서 `from blip import ...` 식의 절대경로 없는
bare import를 쓰고 있어서 (ai/src를 패키지가 아니라 스크립트 실행 위치로
가정한 구조), monorepo 루트가 아니라 `ai/src` 디렉터리 자체를 sys.path에
넣어야 한다.

ai.pipeline.run_pipeline()의 반환 계약 (ai/src/models.py::Event 기준, 2026-08-02
53cc6ef 커밋 시점):
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
          "category": "string | null",   # 더 이상 8개 고정값이 아니라 자유 텍스트.
          ...                             # reservation_number/amount 등 나머지는
                                          # events 테이블이 아직 스텁이라 지금은 사용 안 함.
        },
      },
    }

임베딩(KURE-v1)은 위 docstring 작성 시점엔 이 계약에서 빠져있었지만, ai/src
쪽에서 postprocess를 파일별로 분리하고 KURE 임베딩을 pipeline.py에 연결한
이후로는 반환값 최상위에 "embedding": list[float] | [] 가 추가됐다
(ai/src/pipeline.py::AIPipeline.run 참고, final_event.search_text를 그
자리에서 바로 임베딩). 그래서 이미지 업로드 시의 임베딩은 더 이상
embedding_service.py가 담당하지 않고 이 결과의 embedding 필드를 그대로 쓰면
된다 - embedding_service.py는 이제 검색어(GET /search?q=) 임베딩 전용이다.

event는 events 테이블 대상 데이터다 — events_crud가 아직 스텁이라 지금은 저장하지
않고 호출부에 그대로 전달만 한다. events_crud가 구현되면 라우터에서 event.type이
"none"이 아닐 때만 레코드를 만들면 된다.
"""

import sys
from pathlib import Path
from typing import Optional, TypedDict

# ai/src는 __init__.py가 없는 비-패키지 디렉터리라 `ai.src.pipeline`으로 import할
# 수 없다 — ai/src 자체를 sys.path에 넣고 `pipeline`을 최상위 모듈로 import해야
# pipeline.py 내부의 bare import(`from blip import ...`)도 함께 풀린다.
# backend/app/services/ai_pipeline_service.py -> parents[3] == 모노레포 루트
_AI_SRC_DIR = Path(__file__).resolve().parents[3] / "ai" / "src"
if str(_AI_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SRC_DIR))

try:
    from pipeline import run_pipeline as _run_pipeline
except ImportError:
    _run_pipeline = None


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
    primary_category: Optional[str]
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
    "primary_category": None,
    "search_text": None,
    "embedding": None,
    "event": _EMPTY_EVENT,
}


def run_ai_pipeline(file_bytes: bytes, filename: str) -> AIPipelineResult:
    """
    업로드된 이미지 원본으로 OCR 텍스트/캡션/카테고리/search_text/이벤트 정보를 추출한다.

    ai/src를 import할 수 없는 환경(예: ai/ 없이 backend/만 배포된 Railway,
    또는 모델 의존성이 로컬에 설치 안 된 경우)이거나 파이프라인 실행 자체가
    실패하면 빈 결과로 대체한다. 파이프라인 실패가 업로드 자체를 막아서는 안
    되므로 이 함수는 예외를 던지지 않는다 — 실패 원인은 로깅만 하고 null로
    채운 결과를 반환한다.
    """
    if _run_pipeline is None:
        return _EMPTY_RESULT

    try:
        raw = _run_pipeline(file_bytes)
    except Exception as error:
        print(f"[ai_pipeline_service] run_pipeline 실패: {error}")
        return _EMPTY_RESULT

    event = raw.get("event") or {}
    metadata = event.get("metadata") or {}

    return {
        "ocr_text": raw.get("ocr_text"),
        "caption": raw.get("caption"),
        "primary_category": metadata.get("category"),
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
