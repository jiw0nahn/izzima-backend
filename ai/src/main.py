import json
from pathlib import Path

from qwen import QwenService


OUTPUT_FOLDER = Path("outputs")

TEST_FILES = [
    "29.json",
    "3.json",
    "4.json",
]


def load_ocr_text(json_path: Path) -> str:
    if not json_path.exists():
        raise FileNotFoundError(
            f"OCR JSON 파일을 찾을 수 없습니다: {json_path}"
        )

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    ocr_text = data.get("full_text", "").strip()

    if not ocr_text:
        raise ValueError(
            f"full_text가 비어 있습니다: {json_path}"
        )

    return ocr_text


def main() -> None:
    qwen_service = QwenService()

    for file_name in TEST_FILES:
        json_path = OUTPUT_FOLDER / file_name

        print("\n" + "=" * 60)
        print(f"테스트 파일: {json_path}")
        print("=" * 60)

        try:
            ocr_text = load_ocr_text(json_path)

            event = qwen_service.process(ocr_text)

            print("\n[Event 추출 결과]")
            print(event.model_dump_json(indent=2))

        except Exception as error:
            print(f"\n처리 실패: {error}")


if __name__ == "__main__":
    main()