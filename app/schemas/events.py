"""
app/schemas/events.py

이벤트 조회 응답 Pydantic 모델. events 테이블 컬럼(app/crud/events_crud.py::
create_event의 payload 키)과 1:1 대응한다. 쓰기는 images 라우터의 업로드/삭제
흐름에 붙어 있어 여기는 응답 모델만 둔다.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    id: str
    image_id: str = Field(..., description="이 이벤트가 추출된 원본 이미지의 id.")
    event_type: str = Field(
        ...,
        description=(
            "이벤트 종류. Qwen 구조화 추출 결과 그대로 - expiration/exam/"
            "assignment_due/reservation/departure/check_in/performance/"
            "meeting/schedule 중 하나 (\"none\"은 저장되지 않으므로 나오지 않음)."
        ),
    )
    title: Optional[str] = None
    event_date: Optional[str] = Field(None, description="YYYY-MM-DD, 없으면 null.")
    event_time: Optional[str] = Field(None, description="HH:MM, 없으면 null.")
    location: Optional[str] = None
    is_used: bool = Field(
        False,
        description=(
            "사용자가 상세 화면에서 '사용 완료'로 표시했는지 여부. 이벤트가 "
            "있는 이미지(쿠폰/티켓/예약 등)에만 존재하는 개념이라, 이벤트 "
            "레코드가 없는 이미지(영수증/사진/문서 등)는 애초에 이 필드 자체가 "
            "나오지 않는다(이벤트가 없으므로). 만료 여부는 event_date로 프론트가 "
            "계산하므로 여기서 별도로 내려주지 않는다."
        ),
    )
    created_at: datetime


class EventListResponse(BaseModel):
    data: List[EventResponse]


class EventUsedUpdateRequest(BaseModel):
    is_used: bool = Field(..., description="사용 완료 여부.")
