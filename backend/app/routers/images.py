"""
app/routers/images.py

이미지 관련 라우트.
"""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.crud import images_crud
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
async def upload_image(file: UploadFile = File(...)):
    """
    이미지를 Storage에 업로드하고 images 테이블에 레코드를 생성한다.

    AI Pipeline(OCR/캡션/카테고리/search_text/이벤트)을 호출해 결과를 함께 저장한다.
    다만 파이프라인 모델 자체는 아직 준비되지 않아 run_ai_pipeline()이 항상 빈 값을
    반환하는 스텁 상태. 모델이 준비되면 이 라우트는 그대로 두고 해당 함수 내부만
    바뀌면 됨. KURE-v1 임베딩(image_embeddings 테이블)은 별도 embedding_service의
    책임이라 여기서 다루지 않는다.

    pipeline_result["event"]는 events 테이블 대상 데이터이지만, events_crud가 아직
    스텁이라 지금은 저장하지 않는다 (event.type != "none"일 때 레코드를 만드는 로직은
    events_crud 구현 이후 추가).
    """
    upload_result = await upload_image_to_storage(file)
    storage_path = upload_result["storage_path"]

    pipeline_result = run_ai_pipeline(
        file_bytes=upload_result["file_bytes"], filename=file.filename
    )

    try:
        image = images_crud.create_image(
            storage_path=storage_path,
            ocr_text=pipeline_result["ocr_text"],
            caption=pipeline_result["caption"],
            category=pipeline_result["primary_category"],
            search_text=pipeline_result["search_text"],
        )
    except HTTPException:
        delete_image_from_storage(storage_path)
        raise

    return ImageResponse(**image, signed_url=get_signed_url(storage_path))


@router.get(
    "/images/{image_id}",
    response_model=ImageResponse,
    summary="이미지 상세 조회",
)
def get_image(image_id: str):
    """
    이미지 상세 조회.

    주의: 소유권 검증 없음 -> image_id만 알면 누구나 조회 가능하다.
    auth가 붙기 전까지는 user_id와 요청자를 대조하는 로직이 빠져 있는 상태.
    """
    image = images_crud.get_image(image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return ImageResponse(**image, signed_url=get_signed_url(image["storage_path"]))


@router.patch(
    "/images/{image_id}/category",
    response_model=ImageResponse,
    summary="이미지 카테고리 변경",
)
def update_image_category(image_id: str, body: CategoryUpdateRequest):
    """
    이미지의 category를 사용자가 직접 수정한다.

    AI Pipeline(Qwen)이 잘못 분류했을 때 보정하는 용도. category는 Qwen 구조화
    추출 스펙과 동일한 8개 후보값(coupon/ticket/reservation/academic/receipt/
    document/photo/other)만 허용하며, 그 외 값은 422로 거부됨.

    주의: 소유권 검증 없음 -> image_id만 알면 누구나 변경 가능하다.
    auth가 붙기 전까지는 user_id와 요청자를 대조하는 로직이 빠져 있는 상태.
    """
    image = images_crud.update_image_category(image_id, body.category)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return ImageResponse(**image, signed_url=get_signed_url(image["storage_path"]))


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="이미지 삭제",
)
def delete_image(image_id: str):
    """
    이미지 레코드와 Storage 파일을 함께 삭제한다.

    DB 레코드를 먼저 삭제하고(source of truth), 그다음 Storage 파일 삭제를
    시도한다. Storage 삭제는 delete_image_from_storage 내부에서 실패를 조용히
    무시하므로(이미 없는 파일일 수 있음) 이 라우트를 막지는 않지만, 그만큼
    고아 파일이 남을 가능성은 있음. 지금 단계에서는 별도 정리 배치가 없다.

    image_tags/image_embeddings/events 등 images를 참조할 다른 테이블은 아직
    crud가 스텁이라 여기서 함께 정리하지 않는다.

    주의: 소유권 검증 없음 -> image_id만 알면 누구나 삭제 가능하다.
    auth가 붙기 전까지는 user_id와 요청자를 대조하는 로직이 빠져 있는 상태.
    """
    image = images_crud.delete_image(image_id)
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
):
    """
    이미지 목록 조회 (최신순, 평면 목록).

    아직 다듬어야 할 부분:
    - 카테고리 폴더링 없음: AI Pipeline이 연동되어 category가 채워지기 전까지는 폴더 UI에 쓸 수 없다.
    - 소유권 필터링 없음: auth 붙기 전까지는 user_id로 거르지 않고 전체 이미지를 반환한다.
    - offset 기반 페이지네이션: 이미지 수가 늘어나면 커서 기반으로 바꾸는 게 나을 수 있다.
    """
    images = images_crud.list_images(limit=limit, offset=offset)
    storage_paths = [image["storage_path"] for image in images]
    signed_urls = get_signed_urls(storage_paths)

    return ImageListResponse(
        data=[
            ImageResponse(**image, signed_url=signed_urls.get(image["storage_path"]))
            for image in images
        ]
    )
