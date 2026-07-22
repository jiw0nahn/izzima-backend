"""
app/routers/images.py

이미지 관련 라우트.
"""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.crud import images_crud
from app.services.ai_pipeline_service import run_ai_pipeline
from app.services.storage_service import (
    delete_image_from_storage,
    get_signed_url,
    get_signed_urls,
    upload_image_to_storage,
)

router = APIRouter(tags=["images"])


@router.post("/images")
async def upload_image(file: UploadFile = File(...)):
    """
    이미지를 Storage에 업로드하고 images 테이블에 레코드를 생성한다.

    AI Pipeline(OCR/캡션/카테고리/search_text/이벤트)을 호출해 결과를 함께 저장한다.
    다만 파이프라인 모델 자체는 아직 준비되지 않아 run_ai_pipeline()이 항상 빈 값을
    반환하는 스텁 상태다 — 모델이 준비되면 이 라우트는 그대로 두고 해당 함수 내부만
    바뀌면 된다. KURE-v1 임베딩(image_embeddings 테이블)은 별도 embedding_service의
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

    return {
        "id": image["id"],
        "storage_path": image["storage_path"],
        "created_at": image["created_at"],
        "signed_url": get_signed_url(storage_path),
    }


@router.get("/images/{image_id}")
def get_image(image_id: str):
    """
    이미지 상세 조회.

    주의: 소유권 검증 없음 -> image_id만 알면 누구나 조회 가능하다.
    auth가 붙기 전까지는 user_id와 요청자를 대조하는 로직이 빠져 있는 상태다.
    """
    image = images_crud.get_image(image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return {
        **image,
        "signed_url": get_signed_url(image["storage_path"]),
    }


@router.get("/images")
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

    return {
        "data": [
            {**image, "signed_url": signed_urls.get(image["storage_path"])}
            for image in images
        ]
    }
