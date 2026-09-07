"""
app/services/embedding_service.py

KURE-v1 임베딩 모델 호출 서비스 경계. app/services/ai_pipeline_service.py와 같은
패턴 - HTTP가 아니라 monorepo의 형제 패키지 `ai/src/`를 sys.path에 얹고 bare
import로 함수를 호출한다.

이미지 업로드 시의 임베딩(images.search_text)은 더 이상 이 파일이 담당하지
않는다 - ai/src/pipeline.py::run_pipeline()이 OCR/BLIP/Qwen/후처리에 이어
KURE 임베딩까지 파이프라인 내부에서 직접 계산해 결과에 포함시키도록 바뀌었고
(ai_pipeline_service.py의 AIPipelineResult.embedding), app/routers/images.py는
그 값을 그대로 저장한다. 이 모듈은 오직 **검색어(GET /search?q=) 임베딩**만
담당한다 - 이건 이미지 파이프라인과 무관하게 요청마다 새로 생기는 텍스트라
파이프라인이 대신해줄 수 없다.

ai/src/embedding.py의 실제 인터페이스는 함수가 아니라 클래스다:
    class EmbeddingService:
        def __init__(self) -> None: ...  # SentenceTransformer(KURE-v1) 로딩
        def embed(self, text: str) -> list[float]: ...  # 빈 텍스트면 [] 반환

그래서 모듈 최상위에서 인스턴스를 한 번만 생성해 재사용한다 (매 요청마다 모델을
다시 로딩하면 너무 느림) - ai_pipeline_service.py가 AIPipeline()을 모듈 최상위에서
한 번만 생성하는 것과 같은 패턴.
"""

import sys
from pathlib import Path
from typing import Optional

# backend/app/services/embedding_service.py -> parents[3] == 모노레포 루트
_AI_SRC_DIR = Path(__file__).resolve().parents[3] / "ai" / "src"
if str(_AI_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SRC_DIR))

try:
    from embedding import EmbeddingService as _EmbeddingServiceClass

    _service = _EmbeddingServiceClass()
except Exception as error:
    print(f"[embedding_service] EmbeddingService 초기화 실패: {error}")
    _service = None


def generate_embedding(text: str) -> Optional[list[float]]:
    """
    검색어를 KURE-v1 임베딩 벡터(1024차원, image_embeddings.embedding 컬럼과
    동일한 차원)로 변환한다.

    ai/src를 import할 수 없거나(예: Railway처럼 ai/ 없이 backend/만 배포된 환경)
    모델 로딩 자체가 실패하면(_service가 None) 항상 None을 반환한다 -
    ai_pipeline_service.run_ai_pipeline과 동일한 fail-open 원칙. EmbeddingService.embed()는
    빈 텍스트에 빈 리스트(`[]`)를 반환하는데, 그것도 "임베딩 없음"과 같은 의미이므로
    None으로 통일해서 반환한다.
    """
    if _service is None or not text:
        return None

    try:
        embedding = _service.embed(text)
    except Exception as error:
        print(f"[embedding_service] embed 실패: {error}")
        return None

    return embedding or None
