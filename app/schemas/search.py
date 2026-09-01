"""
app/schemas/search.py

자연어 검색 응답 Pydantic 모델. 검색 결과는 이미지 정보(ImageResponse와 동일한
필드) + 유사도 점수로 구성된다.
"""

from typing import List

from pydantic import BaseModel, Field

from app.schemas.images import ImageResponse


class SearchResultItem(ImageResponse):
    similarity: float = Field(
        ..., description="검색어 임베딩과의 코사인 유사도. 1에 가까울수록 유사함."
    )


class SearchResponse(BaseModel):
    data: List[SearchResultItem]
