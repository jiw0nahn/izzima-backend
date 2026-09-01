"""
app/crud/images_crud.py

`images` 테이블 DB 접근 레이어.
"""

from typing import Optional

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


def create_image(
    storage_path: str,
    user_id: str,
    ocr_text: Optional[str] = None,
    caption: Optional[str] = None,
    category: Optional[str] = None,
    search_text: Optional[str] = None,
) -> dict:
    """
    새 이미지 레코드를 생성한다. user_id는 인증된 요청자의 uuid(필수).

    ocr_text/caption/category/search_text는 AI Pipeline 결과가 있을 때만 채워지고,
    없으면 (파이프라인 미연동 상태 포함) DB 기본값인 null로 남는다.
    """
    supabase = get_supabase_client()
    payload = {"storage_path": storage_path, "user_id": user_id}
    if ocr_text is not None:
        payload["ocr_text"] = ocr_text
    if caption is not None:
        payload["caption"] = caption
    if category is not None:
        payload["category"] = category
    if search_text is not None:
        payload["search_text"] = search_text

    try:
        response = supabase.table("images").insert(payload).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이미지 레코드 저장에 실패했습니다: {str(e)}",
        )

    if not response.data:
        raise HTTPException(
            status_code=502,
            detail="이미지 레코드 저장에 실패했습니다: 응답 데이터가 비어 있습니다.",
        )

    return response.data[0]


def get_image(image_id: str, user_id: str) -> Optional[dict]:
    """
    id로 이미지 레코드 하나를 조회한다. user_id 소유 레코드가 아니면 None을 반환해
    다른 사용자의 이미지 존재 여부 자체가 노출되지 않게 한다 (라우터에서 404 처리).
    """
    supabase = get_supabase_client()
    response = (
        supabase.table("images")
        .select("*")
        .eq("id", image_id)
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else None


def update_image_category(image_id: str, category: str, user_id: str) -> Optional[dict]:
    """
    이미지의 category를 수정한다. 대상 id가 없거나 user_id 소유가 아니면 None
    (라우터에서 404 처리).
    """
    supabase = get_supabase_client()
    try:
        response = (
            supabase.table("images")
            .update({"category": category})
            .eq("id", image_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"카테고리 변경에 실패했습니다: {str(e)}",
        )

    return response.data[0] if response.data else None


def delete_image(image_id: str, user_id: str) -> Optional[dict]:
    """
    이미지 레코드를 삭제한다. 삭제된 레코드를 반환하고, 대상 id가 없거나 user_id
    소유가 아니면 None (라우터에서 404 처리). storage_path가 필요한 호출부가
    Storage 파일도 지울 수 있도록 삭제된 레코드 전체를 반환한다.
    """
    supabase = get_supabase_client()
    try:
        response = (
            supabase.table("images")
            .delete()
            .eq("id", image_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이미지 삭제에 실패했습니다: {str(e)}",
        )

    return response.data[0] if response.data else None


def list_images(user_id: str, limit: int = 20, offset: int = 0) -> list[dict]:
    """
    요청자(user_id) 소유 이미지만 최신순으로 조회한다.

    카테고리 폴더링은 아직 미지원 - AI Pipeline이 연동되기 전이라 모든 레코드의
    category가 null이므로, 지금은 시간순 평면 목록만 제공한다.
    """
    supabase = get_supabase_client()
    response = (
        supabase.table("images")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


def list_all_image_ids(user_id: str) -> list[str]:
    """
    요청자(user_id) 소유 이미지 id를 페이지네이션 없이 전부 조회한다.

    events 조회처럼 "이 사용자의 이미지에 딸린 걸 다 보여줘" 식으로 image_id
    목록 전체가 먼저 필요한 호출부(app/crud/events_crud.py::list_events_by_images)
    전용 - list_images처럼 화면에 그릴 이미지 자체가 필요한 경우에는 페이지네이션이
    있는 list_images를 써야 한다.
    """
    supabase = get_supabase_client()
    response = supabase.table("images").select("id").eq("user_id", user_id).execute()
    return [row["id"] for row in response.data]


def get_images_by_ids(image_ids: list[str]) -> dict[str, dict]:
    """
    id 목록으로 이미지 레코드를 조회해 {id: row} dict로 반환한다.

    호출부(app/routers/search.py)가 이미 embeddings_crud.search_similar_images로
    소유권 필터링과 유사도 순 정렬을 끝낸 상태라고 가정한다 - 이 함수 자체는
    순서를 보장하지 않으므로, 호출부가 매치 순서대로 dict에서 꺼내 써야 한다.
    """
    if not image_ids:
        return {}

    supabase = get_supabase_client()
    response = supabase.table("images").select("*").in_("id", image_ids).execute()
    return {row["id"]: row for row in response.data}
