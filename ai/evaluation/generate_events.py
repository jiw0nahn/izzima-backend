import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
IMAGE_DIR = ROOT_DIR / "images"
OUTPUT_PATH = ROOT_DIR / "evaluation" / "events.json"

sys.path.append(str(SRC_DIR))

from pipeline import run_pipeline


IMAGE_FILES = [
    "0.png",
    "11.png",
    "1.png",
    "29.png",
    "3.png",
    "4.png",
    "6.png",
    "7.png",
    "academic_2.png",
    "academic_6.png",
    "none_2.jpeg",
    "rsv_2.png",
]


def main() -> None:
    results = []

    for image_name in IMAGE_FILES:
        image_path = IMAGE_DIR / image_name

        if not image_path.exists():
            print(f"[SKIP] 이미지 없음: {image_path}")
            continue

        print(f"\n===== {image_name} 처리 중 =====")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        result = run_pipeline(image_bytes)

        results.append(
            {
                "id": image_path.stem,
                "image": image_name,
                "ocr_text": result["ocr_text"],
                "caption": result["caption"],
                "event": result["event"],
                "used_model": result["used_model"],
                "fallback_used": result["fallback_used"],
                "fallback_reasons": result["fallback_reasons"],
            }
        )

        print(f"[DONE] {image_name}")

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()