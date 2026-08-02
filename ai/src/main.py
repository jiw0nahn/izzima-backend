import json
from pathlib import Path

from pipeline import run_pipeline


def main() -> None:
    # main.py 기준으로 테스트 이미지 경로 설정
    image_path = (
        Path("images/4.png")
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"테스트 이미지를 찾을 수 없습니다: {image_path}"
        )

    # 이미지 파일을 bytes 형태로 읽음
    image_bytes = image_path.read_bytes()

    print("===== 입력 이미지 정보 =====")
    print("이미지 경로:", image_path)
    print("image_bytes 타입:", type(image_bytes))
    print("image_bytes 크기:", len(image_bytes), "bytes")

    # 파이프라인 실행
    result = run_pipeline(
        image_bytes=image_bytes,
        caption=None,
    )

    print("\n===== OCR 전체 결과 =====")
    print(
        json.dumps(
            result["ocr_result"],
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\n===== Qwen에 전달된 OCR 텍스트 =====")
    print(result["ocr_text"])

    print("\n===== OCR 텍스트 실제 문자열 구조 =====")
    print(repr(result["ocr_text"]))

    print("\n===== 최종 Event 결과 =====")
    print(
        json.dumps(
            result["event"],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()