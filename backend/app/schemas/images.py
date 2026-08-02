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

# Qwen 구조화 추출 스펙(app/services/ai_pipeline_service.py 상단 docstring)의
# primary_category 후보값과 동일하게 맞춘다. AI Pipeline이 채우는 값과 사용자가
# PATCH로 보정하는 값이 항상 같은 후보 집합을 쓰도록 하기 위함.
CategoryLiteral = Literal[
    "coupon",
    "ticket",
    "reservation",
    "academic",
    "receipt",
    "document",
    "photo",
    "other",
]


class ImageResponse(BaseModel):
    id: str
    user_id: Optional[str] = Field(
        None, description="업로더 id. auth 미도입 상태라 현재는 항상 null."
    )
    storage_path: str = Field(..., description="Supabase Storage 상의 object key.")
    ocr_text: Optional[str] = Field(
        None, description="OCR 추출 텍스트. AI Pipeline 미연동 상태에서는 null."
    )
    caption: Optional[str] = Field(
        None, description="BLIP 캡션. AI Pipeline 미연동 상태에서는 null."
    )
    category: Optional[str] = Field(
        None, description="Qwen 분류 카테고리. AI Pipeline 미연동 상태에서는 null."
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
            "변경할 카테고리. Qwen 구조화 추출 스펙과 동일한 8개 후보값만 허용 "
            "(coupon/ticket/reservation/academic/receipt/document/photo/other)."
        ),
    )
