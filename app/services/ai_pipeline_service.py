"""
app/services/ai_pipeline_service.py

AI Pipeline(OCR -> BLIP -> Qwen2.5-Instruct -> KURE-v1) 호출 서비스 경계.

모델 내부(OCR/캡셔닝/구조화 추출/임베딩 튜닝)는 팀원 담당이므로 이 파일은
그 파이프라인을 "호출"하는 인터페이스만 정의한다. 실제 파이프라인이 아직 준비되지
않았으므로 지금은 항상 빈 결과를 반환하는 스텁이다.

파이프라인이 준비되면 run_ai_pipeline() 내부만 실제 호출로 교체하면 되고,
호출부(images_crud, routers/images.py)는 이 함수의 반환 계약만 지키면 되므로
바뀔 필요가 없다.

반환 계약은 Qwen 구조화 추출 스펙(최종 확정본)을 그대로 따른다:
    {
      "ocr_text": "...",      # PaddleOCR 산출물 (Qwen 입력이자 images.ocr_text)
      "caption": "...",       # BLIP 산출물 (Qwen 입력이자 images.caption)
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
    }

event는 events 테이블 대상 데이터다 — events_crud가 아직 스텁이라 지금은 저장하지
않고 호출부에 그대로 전달만 한다. events_crud가 구현되면 라우터에서 event.type이
"none"이 아닐 때만 레코드를 만들면 된다.

KURE-v1 임베딩 벡터(image_embeddings 테이블 대상)는 이 함수의 반환값에 포함하지
않는다 — 그 저장/검색은 embedding_service.py의 책임 범위다.
"""

from typing import Optional, TypedDict


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


def run_ai_pipeline(file_bytes: bytes, filename: str) -> AIPipelineResult:
    """
    업로드된 이미지 원본으로 OCR 텍스트/캡션/카테고리/search_text/이벤트 정보를 추출한다.

    아직 파이프라인이 연동되지 않아 항상 빈 값을 반환한다 (event.type은 "none").
    실제 연동 이후에도 이 함수는 예외를 던지지 않는 것을 계약으로 유지한다 —
    파이프라인 실패가 업로드 자체를 막아서는 안 되므로, 실패 시에도 null로 채운
    결과를 반환하고 상세 원인은 내부에서 로깅하는 방식으로 구현할 것.
    """
    return {
        "ocr_text": None,
        "caption": None,
        "primary_category": None,
        "search_text": None,
        "event": {
            "type": "none",
            "date": None,
            "time": None,
            "title": None,
            "location": None,
        },
    }
