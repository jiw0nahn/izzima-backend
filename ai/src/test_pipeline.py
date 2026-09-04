import json
from pathlib import Path

from pipeline import run_pipeline


def main():
    image_path = Path("images/4.png")
    image_bytes = image_path.read_bytes()

    result = run_pipeline(image_bytes)

    print("\n===== PIPELINE RESULT =====")

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()