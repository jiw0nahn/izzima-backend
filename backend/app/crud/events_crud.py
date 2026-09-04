"""
app/crud/events_crud.py

`events` 테이블 DB 접근 레이어.

events 테이블은 image_id로만 images를 참조하고 자체 user_id 컬럼이 없다 -
소유권 검증은 호출부가 image_id를 얻기 전에(images_crud.get_image 등으로)
이미 끝냈다고 가정한다.
"""

from datetime import date
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


def get_event(event_id: str) -> Optional[dict]:
    """
    id로 이벤트 레코드 하나를 조회한다. 소유권 검증은 하지 않으므로, 호출부가
    반환된 image_id로 images_crud.get_image를 거쳐 소유권을 확인해야 한다.
    """
    supabase = get_supabase_client()
    response = supabase.table("events").select("*").eq("id", event_id).execute()
    return response.data[0] if response.data else None


def update_event_used(event_id: str, is_used: bool) -> Optional[dict]:
    """
    이벤트의 is_used(사용 완료 여부)를 수정한다. 대상 id가 없으면 None
    (라우터에서 404 처리). 소유권 확인은 호출부 책임(get_event와 마찬가지)
    """
    supabase = get_supabase_client()
    try:
        response = (
            supabase.table("events")
            .update({"is_used": is_used})
            .eq("id", event_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"사용 완료 여부 변경에 실패했습니다: {str(e)}",
        )

    return response.data[0] if response.data else None


def get_events_by_image(image_id: str) -> list[dict]:
    """이미지 하나에 딸린 이벤트 레코드를 전부 조회한다."""
    supabase = get_supabase_client()
    response = (
        supabase.table("events").select("*").eq("image_id", image_id).execute()
    )
    return response.data


def list_events_by_images(image_ids: list[str], upcoming: bool = False) -> list[dict]:
    """
    여러 이미지에 딸린 이벤트를 event_date 오름차순(가까운 D-day가 먼저)으로
    조회한다. Postgres의 ASC 정렬은 기본이 NULLS LAST라 날짜가 없는 이벤트는
    자동으로 뒤로 밀린다.

    upcoming=True면 오늘(date.today()) 이후(당일 포함) event_date를 가진 이벤트만
    남긴다 - 지난 이벤트와 event_date가 없는 이벤트는 D-day 카드 후보가 아니므로
    제외한다. 이 필터는 응답에서만 빠지는 것이지 삭제가 아니라, upcoming=False(기본값)로
    호출하면 지금까지처럼 전부 그대로 조회된다.

    image_ids는 호출부(app/routers/events.py)가 images_crud.list_all_image_ids
    등으로 이미 소유권을 걸러낸 목록이라고 가정한다 - 이 함수 자체는 소유권을
    모른다.
    """
    if not image_ids:
        return []

    supabase = get_supabase_client()
    query = supabase.table("events").select("*").in_("image_id", image_ids)
    if upcoming:
        query = query.gte("event_date", date.today().isoformat())
    response = query.order("event_date").execute()
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
