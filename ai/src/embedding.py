from sentence_transformers import SentenceTransformer


MODEL_NAME = "nlpai-lab/KURE-v1"


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def embed(self, text: str) -> list[float]:
        """
        검색용 텍스트를 KURE-v1 임베딩으로 변환한다.
        """

        if not text or not text.strip():
            return []

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        여러 검색용 텍스트를 한 번에 임베딩한다.
        검색 성능 평가용.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()