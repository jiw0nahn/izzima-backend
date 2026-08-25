"""
app/routers/events.py

이벤트(만료/시험/예약 등) 조회 라우트. 쓰기는 없음 - 생성/삭제는 images
라우터의 업로드/삭제 흐름에 붙어 있다 (app/routers/images.py).
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.crud import events_crud, images_crud
from app.schemas.events import EventListResponse, EventResponse

router = APIRouter(tags=["events"])


@router.get(
    "/images/{image_id}/events",
    response_model=EventListResponse,
    summary="특정 이미지에 딸린 이벤트 조회",
)
def get_events_for_image(image_id: str, user_id: str = Depends(get_current_user_id)):
    """
    이미지 하나에 딸린 이벤트를 전부 반환한다 (현재 업로드 흐름상 보통 0개 또는 1개).

    요청자 소유가 아닌 이미지는 404로 응답한다 (존재 여부 비노출) - images
    라우터와 동일하게, 이벤트를 조회하기 전에 images_crud.get_image로 소유권을
    먼저 확인한다.
    """
    if images_crud.get_image(image_id, user_id) is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    events = events_crud.get_events_by_image(image_id)
    return EventListResponse(data=[EventResponse(**event) for event in events])


@router.get(
    "/events",
    response_model=EventListResponse,
    summary="요청자 전체 이벤트 목록 (D-day 추천 카드용)",
)
def list_events(user_id: str = Depends(get_current_user_id)):
    """
    요청자 소유 이미지에 딸린 이벤트를 전부 event_date 오름차순(가까운 D-day가
    먼저)으로 반환한다. 날짜가 없는 이벤트는 정렬상 뒤로 밀린다.

    추천 카드에 몇 개를 보여줄지, 지난 이벤트를 숨길지 같은 추천 정책은 여기서
    다루지 않는다 - 이 엔드포인트는 순수 조회이고, 정책은 프론트 또는 별도
    추천 로직의 영역.

    지금 단계에서는 사용자당 이미지/이벤트 수가 적다고 보고 페이지네이션 없이
    전체를 반환한다 - 늘어나면 커서 기반으로 바꿔야 할 수 있음.
    """
    image_ids = images_crud.list_all_image_ids(user_id)
    events = events_crud.list_events_by_images(image_ids)
    return EventListResponse(data=[EventResponse(**event) for event in events])
