"""
app/routers/search.py

자연어 이미지 검색 라우트. 검색어를 KURE-v1으로 임베딩해, 업로드 시 저장해둔
image_embeddings와 pgvector 코사인 유사도로 비교한 뒤 가까운 순으로 이미지를
반환한다.

주의: 이 파일 작성 시점 기준 embedding_service.generate_embedding()이 KURE-v1
미연동으로 항상 None을 반환한다 - 그 경우 "결과 없음"과 구분하기 위해 빈 목록이
아니라 503으로 응답한다. 모델이 붙으면 이 라우트는 그대로 두고
embedding_service 내부만 정상 동작하면 된다.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user_id
from app.crud import embeddings_crud, images_crud
from app.schemas.search import SearchResponse, SearchResultItem
from app.services.embedding_service import generate_embedding
from app.services.storage_service import get_signed_urls

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse, summary="자연어 이미지 검색")
def search_images(
    q: str = Query(..., min_length=1, description="검색어 (자연어)"),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """
    검색어를 임베딩해 요청자 소유 이미지 중 코사인 유사도가 가까운 순으로 반환한다.

    embedding_service가 아직 스텁(KURE-v1 미연동)이라 지금은 항상 503으로
    응답한다. 임베딩이 없는(업로드 당시 AI Pipeline이 search_text를 못 뽑았거나
    embedding_service가 실패했던) 이미지는 애초에 image_embeddings에 행이 없어
    검색 대상에서 자연히 빠진다.
    """
    query_embedding = generate_embedding(q)
    if query_embedding is None:
        raise HTTPException(
            status_code=503,
            detail="검색 기능이 아직 준비되지 않았습니다 (임베딩 모델 미연동).",
        )

    matches = embeddings_crud.search_similar_images(user_id, query_embedding, limit)
    if not matches:
        return SearchResponse(data=[])

    image_ids = [match["image_id"] for match in matches]
    images_by_id = images_crud.get_images_by_ids(image_ids)
    signed_urls = get_signed_urls(
        [image["storage_path"] for image in images_by_id.values()]
    )

    results = []
    for match in matches:
        image = images_by_id.get(match["image_id"])
        if image is None:
            continue
        results.append(
            SearchResultItem(
                **image,
                signed_url=signed_urls.get(image["storage_path"]),
                similarity=match["similarity"],
            )
        )

    return SearchResponse(data=results)
