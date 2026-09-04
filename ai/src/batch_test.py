import json
import time
from pathlib import Path

from pipeline import run_pipeline


TEST_IMAGES = [
    Path("images/academic_2.png"),
    Path("images/academic_6.png"),
    Path("images/none_2.jpeg"),
    Path("images/rsv_2.png"),
]


def main() -> None:
    output_dir = Path("outputs/adaptive_batch_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    fallback_count = 0
    success_count = 0
    error_count = 0

    print("=" * 70)
    print("ADAPTIVE PIPELINE TEST")
    print("Primary : qwen3.5:9b")
    print("Fallback: qwen3.5:27b")
    print(f"Test images: {len(TEST_IMAGES)}")
    print("=" * 70)

    total_start = time.time()

    for index, image_path in enumerate(TEST_IMAGES, start=1):
        print()
        print("=" * 70)
        print(f"[{index}/{len(TEST_IMAGES)}] {image_path}")
        print("=" * 70)

        if not image_path.exists():
            print(f"파일 없음: {image_path}")

            all_results.append(
                {
                    "image": str(image_path),
                    "error": "file not found",
                }
            )

            error_count += 1
            continue

        image_bytes = image_path.read_bytes()

        start = time.time()

        try:
            result = run_pipeline(
                image_bytes=image_bytes,
            )

            elapsed = time.time() - start

            used_model = result.get(
                "used_model",
                "unknown",
            )

            fallback_used = result.get(
                "fallback_used",
                False,
            )

            fallback_reasons = result.get(
                "fallback_reasons",
                [],
            )

            if fallback_used:
                fallback_count += 1

            success_count += 1

            print()
            print("===== RESULT =====")
            print(
                json.dumps(
                    result["event"],
                    ensure_ascii=False,
                    indent=2,
                )
            )

            print()
            print("===== PIPELINE INFO =====")
            print(f"최종 사용 모델 : {used_model}")
            print(f"Fallback 사용 : {fallback_used}")

            if fallback_reasons:
                print("Fallback 이유:")

                for reason in fallback_reasons:
                    print(f"- {reason}")

            print(f"처리 시간      : {elapsed:.2f}초")

            record = {
                "image": str(image_path),
                "elapsed_seconds": round(
                    elapsed,
                    2,
                ),
                "used_model": used_model,
                "fallback_used": fallback_used,
                "fallback_reasons": fallback_reasons,
                "ocr_text": result["ocr_text"],
                "caption": result["caption"],
                "event": result["event"],
            }

            all_results.append(record)

        except Exception as error:
            elapsed = time.time() - start

            error_count += 1

            print()
            print(f"ERROR: {error}")
            print(
                f"실패까지 처리 시간: "
                f"{elapsed:.2f}초"
            )

            all_results.append(
                {
                    "image": str(image_path),
                    "elapsed_seconds": round(
                        elapsed,
                        2,
                    ),
                    "error": str(error),
                }
            )

    total_elapsed = time.time() - total_start

    average_elapsed = (
        total_elapsed / success_count
        if success_count > 0
        else 0
    )

    output = {
        "pipeline": {
            "primary_model": "qwen3.5:9b",
            "fallback_model": "qwen3.5:27b",
        },
        "summary": {
            "total_images": len(TEST_IMAGES),
            "success_count": success_count,
            "error_count": error_count,
            "fallback_count": fallback_count,
            "fallback_rate": round(
                fallback_count / success_count,
                4,
            )
            if success_count > 0
            else 0,
            "total_elapsed_seconds": round(
                total_elapsed,
                2,
            ),
            "average_elapsed_seconds": round(
                average_elapsed,
                2,
            ),
        },
        "results": all_results,
    }

    output_path = (
        output_dir
        / "adaptive_pipeline_results.json"
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
    print("=" * 70)
    print("===== SUMMARY =====")
    print(
        f"성공: {success_count}"
        f" / {len(TEST_IMAGES)}"
    )
    print(f"실패: {error_count}")
    print(
        f"Fallback 사용: "
        f"{fallback_count}건"
    )

    if success_count > 0:
        print(
            f"Fallback 비율: "
            f"{fallback_count / success_count * 100:.1f}%"
        )

    print(
        f"전체 처리 시간: "
        f"{total_elapsed:.2f}초"
    )
    print(
        f"평균 처리 시간: "
        f"{average_elapsed:.2f}초"
    )
    print(f"결과 저장: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()