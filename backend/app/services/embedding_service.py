"""
app/services/embedding_service.py

KURE-v1 임베딩 모델 호출 서비스 경계. app/services/ai_pipeline_service.py와 같은
패턴 - HTTP가 아니라 monorepo의 형제 패키지 `ai/src/`를 sys.path에 얹고 bare
import로 함수를 호출한다.

주의 (2026-08-28 작성 시점): ai/src에는 아직 임베딩 모듈이 없다. ai/__pycache__에
예전 구조(ai/embedding.py, ai/src로 재구성되기 전)의 컴파일 흔적만 남아있고
ai/src 쪽에는 재구현되지 않은 상태 - 즉 GPU 서버 Ollama 이슈(Qwen 전용)와는
별개로, 애초에 문진서 쪽에서 KURE-v1 연동 자체를 아직 안 만들었다.

아래 import(`from embedding import embed_text`)는 ai/src의 다른 모듈 이름
규칙(ocr.py/blip.py/qwen.py)에 맞춰 "추정"해서 짜둔 것이고, 실제 파일명/함수
시그니처는 다를 수 있다. ai/src/embedding.py가 생기면 이 파일의 import 문과
_embed_text 호출부만 실제 시그니처에 맞게 고치면 되고, 호출부(라우터/crud)는
건드릴 필요 없다.
"""

import sys
from pathlib import Path
from typing import Optional

# backend/app/services/embedding_service.py -> parents[3] == 모노레포 루트
_AI_SRC_DIR = Path(__file__).resolve().parents[3] / "ai" / "src"
if str(_AI_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SRC_DIR))

try:
    from embedding import embed_text as _embed_text  # 추정 - 실제 모듈 생기면 확인 필요
except ImportError:
    _embed_text = None


def generate_embedding(text: str) -> Optional[list[float]]:
    """
    텍스트(images.search_text 또는 검색어)를 KURE-v1 임베딩 벡터(1024차원,
    image_embeddings.embedding 컬럼과 동일한 차원)로 변환한다.

    ai/src에 임베딩 모듈이 없거나(_embed_text가 None) 호출이 실패하면 None을
    반환한다. ai_pipeline_service.run_ai_pipeline과 동일한 fail-open 원칙 -
    호출부는 None을 받으면 해당 동작(임베딩 저장 또는 검색)을 건너뛰되, 그 자체로
    상위 요청(이미지 업로드 등)을 막아서는 안 된다. 다만 검색 라우터처럼 None이
    "결과 없음"과 구분되어야 하는 곳에서는 호출부가 별도로 처리한다.
    """
    if _embed_text is None or not text:
        return None

    try:
        return _embed_text(text)
    except Exception as error:
        print(f"[embedding_service] embed_text 실패: {error}")
        return None
