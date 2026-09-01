import json
import os
import time
from pathlib import Path

from pipeline import run_pipeline


TEST_IMAGES = [
    Path("images/4.png"),
    Path("images/6.PNG"),
    Path("images/7.png"),
    Path("images/1.PNG"),
    Path("images/29.png"),
]


def main() -> None:
    model_name = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

    output_dir = Path("outputs/batch_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    print("=" * 60)
    print(f"MODEL: {model_name}")
    print(f"TEST IMAGES: {len(TEST_IMAGES)}")
    print("=" * 60)

    total_start = time.time()

    for index, image_path in enumerate(TEST_IMAGES, start=1):
        print()
        print("=" * 60)
        print(f"[{index}/{len(TEST_IMAGES)}] {image_path}")
        print("=" * 60)

        if not image_path.exists():
            print(f"파일 없음: {image_path}")
            continue

        image_bytes = image_path.read_bytes()

        start = time.time()

        try:
            result = run_pipeline(
                image_bytes=image_bytes,
            )

            elapsed = time.time() - start

            record = {
                "image": str(image_path),
                "model": model_name,
                "elapsed_seconds": round(elapsed, 2),
                "ocr_text": result["ocr_text"],
                "caption": result["caption"],
                "event": result["event"],
            }

            all_results.append(record)

            print("\n===== EVENT =====")
            print(
                json.dumps(
                    result["event"],
                    ensure_ascii=False,
                    indent=2,
                )
            )

            print(f"\n처리 시간: {elapsed:.2f}초")

        except Exception as error:
            elapsed = time.time() - start

            print(f"\nERROR: {error}")

            all_results.append(
                {
                    "image": str(image_path),
                    "model": model_name,
                    "elapsed_seconds": round(elapsed, 2),
                    "error": str(error),
                }
            )

    total_elapsed = time.time() - total_start

    output = {
        "model": model_name,
        "total_elapsed_seconds": round(total_elapsed, 2),
        "results": all_results,
    }

    safe_model_name = model_name.replace(":", "_")

    output_path = (
        output_dir / f"results_{safe_model_name}.json"
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print(f"전체 처리 시간: {total_elapsed:.2f}초")
    print(f"결과 저장: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()