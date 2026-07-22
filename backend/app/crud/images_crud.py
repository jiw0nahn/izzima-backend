"""
app/crud/images_crud.py

`images` 테이블 DB 접근 레이어.
"""

from typing import Optional

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


def create_image(
    storage_path: str,
    user_id: Optional[str] = None,
    ocr_text: Optional[str] = None,
    caption: Optional[str] = None,
    category: Optional[str] = None,
    search_text: Optional[str] = None,
) -> dict:
    """
    새 이미지 레코드를 생성한다.

    ocr_text/caption/category/search_text는 AI Pipeline 결과가 있을 때만 채워지고,
    없으면 (파이프라인 미연동 상태 포함) DB 기본값인 null로 남는다.
    """
    supabase = get_supabase_client()
    payload = {"storage_path": storage_path}
    if user_id:
        payload["user_id"] = user_id
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


def get_image(image_id: str) -> Optional[dict]:
    """id로 이미지 레코드 하나를 조회한다. 없으면 None."""
    supabase = get_supabase_client()
    response = supabase.table("images").select("*").eq("id", image_id).execute()
    return response.data[0] if response.data else None


def list_images(limit: int = 20, offset: int = 0) -> list[dict]:
    """
    최신순으로 이미지 레코드 목록을 조회한다.

    카테고리 폴더링은 아직 미지원 - AI Pipeline이 연동되기 전이라 모든 레코드의
    category가 null이므로, 지금은 시간순 평면 목록만 제공한다.
    """
    supabase = get_supabase_client()
    response = (
        supabase.table("images")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data
