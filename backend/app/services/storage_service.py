"""
app/services/storage_service.py

Supabase Storage 연동 서비스. 버킷은 private로 설정되어 있음을 전제로 한다.
- 이미지 업로드
- signed URL 발급 (단건 / 배치)
- 삭제 (업로드 실패 롤백 시 사용)

중요: 이 파일은 "요청받은 storage_path에 대해 signed URL을 만들어주는" 역할만 한다.
"이 사용자가 이 이미지에 접근할 권한이 있는지"는 여기서 검증하지 않는다.
그 소유권 체크는 이 함수를 호출하는 라우터/CRUD 쪽 책임이다 (images 테이블의 user_id 비교 등).
이 함수는 path만 주면 무조건 서명해주는 저수준 유틸리티이므로, 반드시 검증된 path만 넘겨야 한다.

라우터(images.py)나 다른 service에서는 이 모듈의 함수만 호출하면 되고,
Supabase Storage API의 세부 사항(버킷명, path 규칙 등)은 이 파일 안에서만 다룬다.
"""

import uuid
from datetime import datetime

from fastapi import UploadFile, HTTPException
from app.core.supabase_client import get_supabase_client

# 버킷 이름은 Supabase 대시보드에서 미리 생성해두어야 함 (Storage > New bucket, private로 설정)
BUCKET_NAME = "images"

# 허용 확장자 / 최대 용량 (마감 앞두고 최소한의 방어선만)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_FILE_SIZE_MB = 15

# signed URL 기본 유효 시간 (초). 24시간으로 넉넉하게.
# 갤러리 화면 진입 시 한 번 발급받으면 하루 종일 새로고침 없이 볼 수 있는 정도.
DEFAULT_SIGNED_URL_EXPIRES_IN = 60 * 60 * 24


def _build_storage_path(original_filename: str) -> str:
    """
    Storage 상의 저장 경로 생성.
    날짜별 폴더 + uuid로 파일명 충돌 방지.
    예: 2026/07/12/3f2a1c9e.jpg
    """
    ext = "." + original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {ext or '(확장자 없음)'}",
        )

    today = datetime.utcnow().strftime("%Y/%m/%d")
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"{today}/{unique_name}"


async def upload_image_to_storage(file: UploadFile) -> dict:
    """
    이미지를 Supabase Storage(private 버킷)에 업로드하고 storage_path를 반환한다.

    private 버킷이므로 public_url은 더 이상 의미가 없음 — DB에는 이 storage_path만 저장하고,
    실제로 이미지를 보여줘야 할 때 get_signed_url() / get_signed_urls()로 그때그때 발급받는다.

    Returns:
        {
            "storage_path": "2026/07/12/3f2a1c9e.jpg",
            "size_bytes": 123456,
            "file_bytes": b"...",
        }

    file_bytes를 함께 반환하는 이유: UploadFile은 한 번 read()하면 다시 읽을 수 없어서,
    호출부(라우터)가 AI Pipeline에 같은 파일을 넘기려면 여기서 이미 읽은 바이트를 재사용해야 한다.

    Raises:
        HTTPException: 확장자 위반, 용량 초과, 업로드 실패 시
    """
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"파일 용량이 너무 큽니다 ({size_mb:.1f}MB). 최대 {MAX_FILE_SIZE_MB}MB까지 허용됩니다.",
        )

    storage_path = _build_storage_path(file.filename)
    content_type = file.content_type or "application/octet-stream"

    supabase = get_supabase_client()

    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": content_type},
        )
    except Exception as e:
        # supabase-py는 실패 시 StorageException을 던짐. 원인 그대로 노출하지 않고 래핑.
        raise HTTPException(
            status_code=502,
            detail=f"이미지 업로드에 실패했습니다: {str(e)}",
        )

    return {
        "storage_path": storage_path,
        "size_bytes": len(file_bytes),
        "file_bytes": file_bytes,
    }


def get_signed_url(
    storage_path: str,
    expires_in: int = DEFAULT_SIGNED_URL_EXPIRES_IN,
) -> str:
    """
    단일 이미지에 대한 signed URL을 발급한다.
    이미지 상세 화면처럼 한 장만 보여줄 때 사용.

    주의: 이 함수는 storage_path가 유효한지, 호출자가 이 이미지의 소유자인지 확인하지 않는다.
    반드시 라우터에서 images 테이블의 user_id와 요청자를 대조한 뒤에만 호출할 것.
    """
    supabase = get_supabase_client()
    try:
        result = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            storage_path, expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이미지 URL 발급에 실패했습니다: {str(e)}",
        )
    return result["signedURL"]


def get_signed_urls(
    storage_paths: list[str],
    expires_in: int = DEFAULT_SIGNED_URL_EXPIRES_IN,
) -> dict[str, str]:
    """
    여러 이미지에 대한 signed URL을 한 번의 API 호출로 배치 발급한다.
    갤러리 목록처럼 여러 장을 한 번에 보여줄 때 사용 — 장수만큼 반복 호출하지 말 것.

    Returns:
        {storage_path: signed_url, ...} 형태의 매핑.
        일부 path가 존재하지 않으면 해당 항목은 결과에서 빠질 수 있음.

    주의: get_signed_url과 동일하게 소유권 검증은 호출자 책임.
    """
    if not storage_paths:
        return {}

    supabase = get_supabase_client()
    try:
        results = supabase.storage.from_(BUCKET_NAME).create_signed_urls(
            storage_paths, expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"이미지 URL 일괄 발급에 실패했습니다: {str(e)}",
        )

    return {
        item["path"]: item["signedURL"]
        for item in results
        if item.get("signedURL")
    }


def delete_image_from_storage(storage_path: str) -> None:
    """
    업로드 이후 단계(DB insert, AI 파이프라인 등)에서 실패했을 때
    Storage에 남은 파일을 정리하기 위한 롤백용 함수.
    삭제 실패는 조용히 무시 (이미 없는 파일일 수도 있으므로 흐름을 막지 않음).
    """
    supabase = get_supabase_client()
    try:
        supabase.storage.from_(BUCKET_NAME).remove([storage_path])
    except Exception:
        pass