"""
test_storage_upload.py

storage_service.py를 FastAPI 서버 없이 단독으로 테스트하는 스크립트.

사용법:
    python test_storage_upload.py <이미지_파일_경로>

예:
    python test_storage_upload.py ./sample.jpg

프로젝트 루트(backend/)에서 실행해야 함 (app 모듈을 import 하기 때문).
"""

import asyncio
import mimetypes
import sys
from pathlib import Path

from starlette.datastructures import Headers, UploadFile

from app.services.storage_service import (
    upload_image_to_storage,
    get_signed_url,
    delete_image_from_storage,
)


async def main(image_path: str) -> None:
    path = Path(image_path)
    if not path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        sys.exit(1)

    content_type, _ = mimetypes.guess_type(path.name)
    content_type = content_type or "application/octet-stream"

    print(f"업로드 시작: {path.name} ({path.stat().st_size / 1024:.1f} KB, {content_type})")

    with open(path, "rb") as f:
        upload_file = UploadFile(
            filename=path.name,
            file=f,
            headers=Headers({"content-type": content_type}),
        )

        try:
            result = await upload_image_to_storage(upload_file)
        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            sys.exit(1)

    print("\n✅ 업로드 성공!")
    print(f"  storage_path : {result['storage_path']}")
    print(f"  size_bytes   : {result['size_bytes']}")

    # private 버킷이므로 별도로 signed URL을 발급받아야 브라우저에서 열림
    signed_url = get_signed_url(result["storage_path"], expires_in=300)  # 테스트용 5분
    print(f"\n  signed_url (5분간 유효): {signed_url}")
    print("\n위 signed_url을 브라우저 주소창에 붙여넣어서 이미지가 뜨는지 확인하세요.")
    print("5분 지나면 같은 URL로는 안 열려야 정상입니다 (만료 확인용).")
    print("Supabase 대시보드 → Storage → images 버킷에서도 파일이 생겼는지 확인해보세요.\n")

    answer = input("방금 올린 테스트 파일을 삭제할까요? (y/n): ").strip().lower()
    if answer == "y":
        delete_image_from_storage(result["storage_path"])
        print("🗑️  삭제 완료")
    else:
        print("삭제하지 않았습니다. 필요하면 대시보드에서 수동으로 지우세요.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python test_storage_upload.py <이미지_파일_경로>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))