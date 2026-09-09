"""
app/schemas/images.py

이미지 관련 응답 Pydantic 모델.
업로드/상세/목록 세 라우트가 이 스키마들을 공유하며, 프론트엔드와의 안정적인
응답 계약 역할을 한다 (AI Pipeline 미연동 상태에서는 ocr_text/caption/category/
search_text가 항상 null로 내려간다).
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# ai/src/models.py::EventType과 동일한 값 집합.
# 예전에는 별도의 Qwen category 후보값을 썼는데 event.type과 의미 중복으로 category 필드 아예 삭제.
# event.type을 그대로 대신 씀. AI Pipeline이 채우는 값과 사용자가 PATCH로 보정하는 값이 항상같은
# 집합을 쓰도록 EventType과 맞춰둔다.
CategoryLiteral = Literal[
    "expiration",
    "exam",
    "assignment_due",
    "reservation",
    "departure",
    "check_in",
    "performance",
    "meeting",
    "schedule",
    "none",
]


class ImageResponse(BaseModel):
    id: str
    user_id: Optional[str] = Field(
        None, description="업로더 uuid. 인증 토큰(sub claim)에서 추출된 값."
    )
    storage_path: str = Field(..., description="Supabase Storage 상의 object key.")
    ocr_text: Optional[str] = Field(
        None, description="OCR 추출 텍스트. AI Pipeline 미연동 상태에서는 null."
    )
    caption: Optional[str] = Field(
        None, description="BLIP 캡션. AI Pipeline 미연동 상태에서는 null."
    )
    category: Optional[str] = Field(
        None, description="AI가 추출한 이벤트 타입(EventType) 값. AI Pipeline 미연동 상태에서는 null."
    )
    search_text: Optional[str] = Field(
        None, description="자연어 검색용 텍스트. AI Pipeline 미연동 상태에서는 null."
    )
    created_at: datetime
    signed_url: Optional[str] = Field(
        None,
        description=(
            "private 버킷의 임시 서명 URL (기본 24시간 유효). "
            "요청 시점에 발급되므로 캐시/영구 저장 금지. "
            "서명 발급 자체가 실패한 개별 항목은 null일 수 있음."
        ),
    )


class ImageListResponse(BaseModel):
    data: List[ImageResponse]


class CategoryUpdateRequest(BaseModel):
    category: CategoryLiteral = Field(
        ...,
        description=(
            "변경할 category 값. ai/src/models.py::EventType과 동일한 10개 후보값만 "
            "허용 (expiration/exam/assignment_due/reservation/departure/check_in/"
            "performance/meeting/schedule/none)."
        ),
    )
