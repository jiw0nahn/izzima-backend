"""
app/routers/images.py

이미지 관련 라우트.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.core.security import get_current_user_id
from app.crud import embeddings_crud, events_crud, images_crud
from app.schemas.images import CategoryUpdateRequest, ImageListResponse, ImageResponse
from app.services.ai_pipeline_service import run_ai_pipeline
from app.services.storage_service import (
    delete_image_from_storage,
    get_signed_url,
    get_signed_urls,
    upload_image_to_storage,
)

router = APIRouter(tags=["images"])


@router.post(
    "/images",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="이미지 업로드",
)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """
    이미지를 Storage에 업로드하고 images 테이블에 레코드를 생성한다.
    레코드의 user_id는 인증 토큰에서 추출한 요청자 uuid로 채워진다.

    AI Pipeline(OCR/캡션/category(=event.type)/search_text/이벤트)을 호출해 결과를
    함께 저장한다. GPU 서버와의 연결이 안 됐다면 run_ai_pipeline()이 현재는 항상
    빈 값을 반환한다.

    pipeline_result["event"].type이 "none"이 아니면 events 테이블에도 레코드를
    생성한다. pipeline_result["embedding"]이 있으면 image_embeddings에도 저장한다.
    이벤트/임베딩 저장 실패는 이미지 업로드 자체를 막지 않고, 로그만 남기고 넘어감).
    """
    upload_result = await upload_image_to_storage(file)
    storage_path = upload_result["storage_path"]

    pipeline_result = run_ai_pipeline(
        file_bytes=upload_result["file_bytes"], filename=file.filename
    )
    event = pipeline_result["event"]

    try:
        image = images_crud.create_image(
            storage_path=storage_path,
            user_id=user_id,
            ocr_text=pipeline_result["ocr_text"],
            caption=pipeline_result["caption"],
            category=event["type"] if event["type"] != "none" else None,
            search_text=pipeline_result["search_text"],
        )
    except HTTPException:
        delete_image_from_storage(storage_path)
        raise

    if event["type"] != "none":
        try:
            events_crud.create_event(
                image_id=image["id"],
                event_type=event["type"],
                event_date=event["date"],
                event_time=event["time"],
                title=event["title"],
                location=event["location"],
            )
        except HTTPException as e:
            print(f"[images router] 이벤트 저장 실패: {e.detail}")

    embedding = pipeline_result["embedding"]
    if embedding is not None:
        try:
            embeddings_crud.create_embedding(image["id"], embedding)
        except HTTPException as e:
            print(f"[images router] 임베딩 저장 실패: {e.detail}")

    return ImageResponse(**image, signed_url=get_signed_url(storage_path))


@router.get(
    "/images/{image_id}",
    response_model=ImageResponse,
    summary="이미지 상세 조회",
)
def get_image(image_id: str, user_id: str = Depends(get_current_user_id)):
    """
    이미지 상세 조회.

    요청자 소유가 아닌 이미지는 존재 여부를 노출하지 않기 위해 다른 사용자의
    이미지와 동일하게 404로 응답한다 (403이 아님).
    """
    image = images_crud.get_image(image_id, user_id)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return ImageResponse(**image, signed_url=get_signed_url(image["storage_path"]))


@router.patch(
    "/images/{image_id}/category",
    response_model=ImageResponse,
    summary="이미지 카테고리 변경",
)
def update_image_category(
    image_id: str,
    body: CategoryUpdateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    이미지의 category를 사용자가 직접 수정한다.

    AI Pipeline이 잘못 분류했을 때 보정하는 용도.
    category는 EventType과 동일한 10개 후보값(expiration/exam/assignment_due/reservation/
    departure/check_in/performance/meeting/schedule/none)만 허용하며, 그 외 값은
    422로 거부됨.

    요청자 소유가 아닌 이미지는 404로 응답한다 (존재 여부 비노출).
    """
    image = images_crud.update_image_category(image_id, body.category, user_id)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return ImageResponse(**image, signed_url=get_signed_url(image["storage_path"]))


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="이미지 삭제",
)
def delete_image(image_id: str, user_id: str = Depends(get_current_user_id)):
    """
    이미지 레코드와 Storage 파일을 함께 삭제한다.

    events/image_embeddings 테이블이 image_id로 images를 참조하는 FK를 가지고
    있어(cascade 미설정), 이미지 레코드를 지우기 전에 딸린 이벤트/임베딩부터
    먼저 정리한다. 소유권 확인도 그 전에 끝내야, 존재하지 않거나 남의 이미지
    id로 이벤트/임베딩만 지워지는 일이 없다. 그 다음 이미지 레코드를
    삭제하고(source of truth), 마지막으로 Storage 파일 삭제를 시도한다. Storage
    삭제는 delete_image_from_storage 내부에서 실패를 조용히 무시하므로(이미
    없는 파일일 수 있음) 이 라우트를 막지는 않지만, 그만큼 고아 파일이 남을
    가능성은 있음. 지금 단계에서는 별도 정리 배치가 없다.

    image_tags 등 images를 참조할 다른 테이블은 아직 여기서 함께 정리하지 않는다
    (테이블 자체가 아직 crud/router 없음).

    요청자 소유가 아닌 이미지는 404로 응답한다 (존재 여부 비노출).
    """
    if images_crud.get_image(image_id, user_id) is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    events_crud.delete_events_by_image(image_id)
    embeddings_crud.delete_embedding_by_image(image_id)

    image = images_crud.delete_image(image_id, user_id)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    delete_image_from_storage(image["storage_path"])


@router.get(
    "/images",
    response_model=ImageListResponse,
    summary="이미지 목록 조회",
)
def list_images(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
):
    """
    요청자 소유 이미지 목록 조회 (최신순, 평면 목록).

    아직 다듬어야 할 부분:
        offset 기반 페이지네이션: 이미지 수가 늘어나면 커서 기반으로 바꾸는 게 나을 수 있다.
    """
    images = images_crud.list_images(user_id=user_id, limit=limit, offset=offset)
    storage_paths = [image["storage_path"] for image in images]
    signed_urls = get_signed_urls(storage_paths)

    return ImageListResponse(
        data=[
            ImageResponse(**image, signed_url=signed_urls.get(image["storage_path"]))
            for image in images
        ]
    )
