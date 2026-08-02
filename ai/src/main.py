import json
from pathlib import Path

from pipeline import run_pipeline


def main() -> None:
    image_path = Path("images/4.png")

    if not image_path.exists():
        raise FileNotFoundError(
            f"테스트 이미지를 찾을 수 없습니다: {image_path}"
        )

    image_bytes = image_path.read_bytes()

    print("===== 입력 이미지 정보 =====")
    print("이미지 경로:", image_path)
    print("image_bytes 타입:", type(image_bytes))
    print("image_bytes 크기:", len(image_bytes), "bytes")

    # caption=None 제거
    result = run_pipeline(
        image_bytes=image_bytes,
    )

    print("\n===== OCR TEXT =====")
    print(result["ocr_text"])

    print("\n===== BLIP CAPTION =====")
    print(result["caption"])

    print("\n===== EVENT =====")
    print(
        json.dumps(
            result["event"],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()