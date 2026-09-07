import json
import sys
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
EVAL_DIR = ROOT_DIR / "evaluation"

sys.path.append(str(SRC_DIR))

from embedding import EmbeddingService
from models import Event
from postprocess.search_text import (
    build_search_text_v1,
    build_search_text_v2,
    build_search_text_v3,
    build_search_text_v4,
    build_search_text_v5,
    build_search_text_v6,
)


EVENTS_PATH = EVAL_DIR / "test_events.json"
QUERIES_PATH = EVAL_DIR / "queries_test.json"


def cosine_similarity(
    query_embedding: np.ndarray,
    event_embeddings: np.ndarray,
) -> np.ndarray:
    # 이미 normalize_embeddings=True 이므로
    # dot product = cosine similarity
    return event_embeddings @ query_embedding


def build_search_text(
    version: int,
    event: Event,
    caption: str | None,
    ocr_text: str | None,
) -> str:
    if version == 1:
        return build_search_text_v1(event)

    if version == 2:
        return build_search_text_v2(event)

    if version == 3:
        return build_search_text_v3(event)

    if version == 4:
        return build_search_text_v4(
            event,
            caption,
        )

    if version == 5:
        return build_search_text_v5(
            event,
            caption,
            ocr_text,
        )

    if version == 6:
        return build_search_text_v6(
            event,
            caption,
            ocr_text,
        )

    raise ValueError(
        f"Unsupported version: {version}"
    )


def evaluate_version(
    version: int,
    events_data: list[dict],
    queries_data: list[dict],
    embedding_service: EmbeddingService,
) -> dict:
    event_ids = []
    search_texts = []

    for item in events_data:
        event = Event.model_validate(
            item["event"]
        )

        search_text = build_search_text(
            version=version,
            event=event,
            caption=item.get("caption"),
            ocr_text=item.get("ocr_text")
        )

        event_ids.append(item["id"])
        search_texts.append(search_text)

    event_embeddings = np.array(
        embedding_service.embed_batch(
            search_texts
        )
    )

    hit_at_1 = 0
    hit_at_3 = 0
    reciprocal_rank_sum = 0.0

    query_results = []

    for query_item in queries_data:
        query = query_item["query"]
        target_id = query_item["target_id"]

        query_embedding = np.array(
            embedding_service.embed(query)
        )

        similarities = cosine_similarity(
            query_embedding,
            event_embeddings,
        )

        ranked_indices = np.argsort(
            similarities
        )[::-1]

        ranked_ids = [
            event_ids[index]
            for index in ranked_indices
        ]

        target_rank = ranked_ids.index(
            target_id
        ) + 1

        if target_rank == 1:
            hit_at_1 += 1

        if target_rank <= 3:
            hit_at_3 += 1

        reciprocal_rank_sum += (
            1.0 / target_rank
        )

        query_results.append(
            {
                "query": query,
                "target_id": target_id,
                "rank": target_rank,
                "top3": ranked_ids[:3],
            }
        )

    total = len(queries_data)

    return {
        "version": version,
        "recall@1": hit_at_1 / total,
        "recall@3": hit_at_3 / total,
        "mrr": reciprocal_rank_sum / total,
        "query_results": query_results,
    }


def main() -> None:
    with open(
        EVENTS_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        events_data = json.load(f)

    with open(
        QUERIES_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        queries_data = json.load(f)

    embedding_service = EmbeddingService()

    all_results = []

    for version in [1, 2, 3, 4, 5, 6]:
        print(
            f"\n===== search_text v{version} 평가 ====="
        )

        result = evaluate_version(
            version=version,
            events_data=events_data,
            queries_data=queries_data,
            embedding_service=embedding_service,
        )

        all_results.append(result)

        print(
            f"Recall@1: "
            f"{result['recall@1']:.4f}"
        )
        print(
            f"Recall@3: "
            f"{result['recall@3']:.4f}"
        )
        print(
            f"MRR: "
            f"{result['mrr']:.4f}"
        )

    output_path = (
        EVAL_DIR / "search_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            all_results,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"\n상세 결과 저장 완료: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()