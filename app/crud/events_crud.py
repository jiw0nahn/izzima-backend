"""
app/crud/events_crud.py

`events` 테이블 DB 접근 레이어.

events 테이블은 image_id로만 images를 참조하고 자체 user_id 컬럼이 없다 -
소유권 검증은 호출부가 image_id를 얻기 전에(images_crud.get_image 등으로)
이미 끝냈다고 가정한다.
"""

from typing import Optional

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


def create_event(
    image_id: str,
    event_type: str,
    event_date: Optional[str] = None,
    event_time: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
) -> dict:
    """
    이미지 하나에 대한 이벤트 레코드를 생성한다.

    event_type이 "none"인 경우까지 저장할지는 호출부(라우터) 판단 영역이라
    이 함수는 별도 필터링 없이 그대로 insert한다.
    """
    supabase = get_supabase_client()
    payload = {"image_id": image_id, "event_type": event_type}
    if event_date is not None:
        payload["event_date"] = event_date
    if event_time is not None:
        payload["event_time"] = event_time
    if title is not None:
        payload["title"] = title
    if location is not None:
        payload["location"] = location

    try:
        response = supabase.table("events").insert(payload).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이벤트 레코드 저장에 실패했습니다: {str(e)}",
        )

    if not response.data:
        raise HTTPException(
            status_code=502,
            detail="이벤트 레코드 저장에 실패했습니다: 응답 데이터가 비어 있습니다.",
        )

    return response.data[0]


def get_events_by_image(image_id: str) -> list[dict]:
    """이미지 하나에 딸린 이벤트 레코드를 전부 조회한다."""
    supabase = get_supabase_client()
    response = (
        supabase.table("events").select("*").eq("image_id", image_id).execute()
    )
    return response.data


def delete_events_by_image(image_id: str) -> None:
    """이미지 삭제 시 함께 정리하기 위해 image_id에 딸린 이벤트를 전부 삭제한다."""
    supabase = get_supabase_client()
    try:
        supabase.table("events").delete().eq("image_id", image_id).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이벤트 레코드 삭제에 실패했습니다: {str(e)}",
        )
