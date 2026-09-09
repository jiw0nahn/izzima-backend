"""
app/services/embedding_service.py

KURE-v1 검색어 임베딩 호출 서비스 경계. app/services/ai_pipeline_service.py와
AI 서버에 HTTP로 요청한다.

POST {AI_SERVER_URL}/embed-query 계약 (직접 호출해서 확인함):
    요청 body: {"query": "<검색어>"}
    응답: {"query": "<검색어>", "embedding": [float, ...]}  # 1024차원
"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "").rstrip("/")

_REQUEST_TIMEOUT_SECONDS = 30.0


def generate_embedding(text: str) -> Optional[list[float]]:
    """
    검색어를 KURE-v1 임베딩 벡터(1024차원)로 변환한다.

    AI_SERVER_URL이 설정 안 되어 있거나, 그 서버 호출이 실패하면 None을 반환한다
    호출부(검색 라우터)는 None을 "결과 없음"과 구분해서 503으로 응답한다.
    """
    if not AI_SERVER_URL or not text:
        return None

    try:
        response = httpx.post(
            f"{AI_SERVER_URL}/embed-query",
            json={"query": text},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
    except Exception as error:
        print(f"[embedding_service] AI 서버 호출 실패: {error}")
        return None

    return embedding or None
