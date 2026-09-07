"""
app/services/embedding_service.py

KURE-v1 검색어 임베딩 호출 서비스 경계. app/services/ai_pipeline_service.py와
같은 패턴 - 직접 import가 아니라 AI 서버(GPU 서버, Cloudflare Tunnel로 노출됨)에
HTTP로 요청한다.

이미지 업로드 시의 임베딩(images.search_text)은 이 파일이 담당하지 않는다 -
ai_pipeline_service.py의 POST {AI_SERVER_URL}/analyze가 OCR/BLIP/Qwen/후처리에
이어 KURE 임베딩까지 한 번에 계산해서 돌려주고, app/routers/images.py는 그 값을
그대로 저장한다. 이 모듈은 오직 **검색어(GET /search?q=) 임베딩**만 담당한다 -
이건 이미지 파이프라인과 무관하게 요청마다 새로 생기는 텍스트라 파이프라인이
대신해줄 수 없다.

이전에는(2026-09-07 이전) ai/src/embedding.py를 sys.path 트릭으로 직접
import해서 호출했는데, 이러면 backend 프로세스가 ai/의 무거운 의존성이 설치된
환경(GPU 서버 등)에서만 동작했다 - Railway나 일반 로컬 개발 환경에서는 항상
실패했다. 진서님이 AI 서버에 텍스트 전용 임베딩 엔드포인트
`POST {AI_SERVER_URL}/embed-query`를 추가해줘서, ai_pipeline_service.py와
동일하게 HTTP 호출로 전환한다.

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
    검색어를 KURE-v1 임베딩 벡터(1024차원, image_embeddings.embedding 컬럼과
    동일한 차원)로 변환한다.

    AI_SERVER_URL이 설정 안 되어 있거나, 그 서버 호출이 실패하면 None을 반환한다
    - ai_pipeline_service.run_ai_pipeline과 동일한 fail-open 원칙. 호출부(검색
    라우터)는 None을 "결과 없음"과 구분해서 503으로 응답한다.
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
