"""
app/crud/embeddings_crud.py

`image_embeddings` 테이블 DB 접근 레이어. embedding 컬럼은 pgvector
vector(1024) - KURE-v1 임베딩 차원과 일치한다.

images와 마찬가지로 이 테이블도 자체 user_id 컬럼이 없다 - 소유권 검증은
호출부가 image_id를 얻기 전에 이미 끝냈다고 가정한다.
"""

from typing import Optional

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


def create_embedding(image_id: str, embedding: list[float]) -> dict:
    """이미지 하나에 대한 임베딩 벡터를 저장한다."""
    supabase = get_supabase_client()
    payload = {"image_id": image_id, "embedding": embedding}

    try:
        response = supabase.table("image_embeddings").insert(payload).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"임베딩 저장에 실패했습니다: {str(e)}",
        )

    if not response.data:
        raise HTTPException(
            status_code=502,
            detail="임베딩 저장에 실패했습니다: 응답 데이터가 비어 있습니다.",
        )

    return response.data[0]


def get_embedding_by_image(image_id: str) -> Optional[dict]:
    """이미지 하나에 대한 임베딩 레코드를 조회한다. 없으면 None."""
    supabase = get_supabase_client()
    response = (
        supabase.table("image_embeddings")
        .select("*")
        .eq("image_id", image_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_embedding_by_image(image_id: str) -> None:
    """이미지 삭제 시 함께 정리하기 위해 image_id에 딸린 임베딩을 삭제한다."""
    supabase = get_supabase_client()
    try:
        supabase.table("image_embeddings").delete().eq(
            "image_id", image_id
        ).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"임베딩 삭제에 실패했습니다: {str(e)}",
        )


def search_similar_images(
    user_id: str, query_embedding: list[float], limit: int = 20
) -> list[dict]:
    """
    query_embedding과 코사인 유사도가 가까운 순으로 요청자 소유 이미지의
    image_id/similarity를 반환한다 ([{"image_id": ..., "similarity": ...}, ...]).

    image_embeddings에는 user_id 컬럼이 없고, postgrest 클라이언트로는 pgvector
    거리 연산(`<=>`)과 images 테이블 join을 동시에 표현할 수 없어서, Supabase에
    미리 만들어둔 `match_images` Postgres 함수를 rpc로 호출한다.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.rpc(
            "match_images",
            {
                "query_embedding": query_embedding,
                "match_user_id": user_id,
                "match_count": limit,
            },
        ).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"유사 이미지 검색에 실패했습니다: {str(e)}",
        )

    return response.data
